"""
FastAPI Server for PromptCraft Integration

Provides RESTful API endpoints for route analysis, smart execution,
and model management, integrating with zen-mcp-server's dynamic routing system.
"""

import asyncio
import logging
import os
import threading
import time
import uvicorn
from contextlib import asynccontextmanager
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import zen-mcp-server routing components
from routing.model_level_router import ModelLevelRouter, ModelLevel
from routing.complexity_analyzer import ComplexityAnalyzer, TaskType

logger = logging.getLogger(__name__)

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

# Pydantic models for API requests/responses
class RouteAnalysisRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to analyze")
    user_tier: str = Field(..., description="User tier: free|limited|full|premium|admin")
    task_type: Optional[str] = Field(None, description="Optional task type hint")

class SmartExecutionRequest(BaseModel):
    prompt: str = Field(..., description="The enhanced prompt from Journey 1")
    user_tier: str = Field(..., description="User tier: free|limited|full|premium|admin")
    channel: str = Field("stable", description="Model channel: stable|experimental")
    cost_optimization: bool = Field(True, description="Enable cost optimization")
    include_reasoning: bool = Field(True, description="Include reasoning in response")

class ModelListRequest(BaseModel):
    user_tier: Optional[str] = Field(None, description="Filter by user tier")
    channel: str = Field("stable", description="Model channel: stable|experimental")
    include_metadata: bool = Field(True, description="Include detailed metadata")
    format: str = Field("ui", description="Response format: ui|api")

class PromptCraftAPIServer:
    """
    FastAPI server providing PromptCraft integration endpoints.
    
    Integrates with existing zen-mcp-server routing infrastructure
    while providing external HTTP API access.
    """
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.model_router = ModelLevelRouter()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.app = None
        self.server = None
        self.server_thread = None
        self.running = False
        
        # Performance metrics
        self.request_count = 0
        self.successful_requests = 0
        self.total_response_time = 0.0
        
        self._setup_app()
    
    def _setup_app(self):
        """Initialize FastAPI application with middleware and routes."""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """Manage application startup and shutdown."""
            logger.info("🚀 PromptCraft API Server starting...")
            yield
            logger.info("🛑 PromptCraft API Server shutting down...")
        
        # Create FastAPI app
        self.app = FastAPI(
            title="PromptCraft API",
            description="Zen MCP Server integration endpoints for PromptCraft",
            version="1.0.0",
            lifespan=lifespan
        )
        
        # Add rate limiting
        self.app.state.limiter = limiter
        self.app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        # Add CORS middleware
        allowed_origins = [
            "http://localhost:7860",  # Default PromptCraft origin
            os.getenv("PROMPTCRAFT_ORIGIN", "http://localhost:7860")
        ]
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )
        
        # Add request timing middleware
        @self.app.middleware("http")
        async def add_request_timing(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Update metrics
            self.request_count += 1
            if 200 <= response.status_code < 400:
                self.successful_requests += 1
            self.total_response_time += process_time
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register all API endpoints."""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint for monitoring."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "promptcraft-api",
                "version": "1.0.0"
            }
        
        @self.app.post("/api/promptcraft/route/analyze")
        @limiter.limit("100/minute")
        async def analyze_route(request: Request, data: RouteAnalysisRequest):
            """
            Analyze prompt complexity and provide model recommendations.
            
            This endpoint performs complexity analysis and returns routing recommendations
            without actually executing the prompt.
            """
            try:
                start_time = time.time()
                
                # Analyze prompt complexity
                analysis = await self._analyze_prompt_complexity(data.prompt, data.task_type)
                
                # Get routing recommendations
                recommendations = await self._get_routing_recommendations(
                    analysis, data.user_tier
                )
                
                processing_time = time.time() - start_time
                
                return {
                    "success": True,
                    "analysis": {
                        "task_type": analysis["task_type"],
                        "complexity_score": analysis["complexity_score"],
                        "complexity_level": analysis["complexity_level"],
                        "indicators": analysis.get("indicators", []),
                        "reasoning": analysis.get("reasoning", "")
                    },
                    "recommendations": recommendations,
                    "processing_time": processing_time
                }
                
            except Exception as e:
                logger.error(f"Route analysis error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/promptcraft/execute/smart")
        @limiter.limit("100/minute")
        async def smart_execution(request: Request, data: SmartExecutionRequest):
            """
            Route and execute prompt in a single call with intelligence.
            
            This endpoint combines complexity analysis, model selection, and execution
            for seamless integration with PromptCraft applications.
            """
            try:
                start_time = time.time()
                
                # Analyze prompt complexity
                analysis = await self._analyze_prompt_complexity(data.prompt)
                
                # Select optimal model
                selected_model = await self._select_optimal_model(
                    analysis, data.user_tier, data.channel, data.cost_optimization
                )
                
                # Execute with selected model
                execution_result = await self._execute_with_model(
                    data.prompt, selected_model, analysis
                )
                
                processing_time = time.time() - start_time
                
                # Update model usage stats if experimental
                if data.channel == "experimental":
                    self.data_manager.update_model_usage(
                        selected_model["id"], 
                        execution_result["success"]
                    )
                
                return {
                    "success": True,
                    "result": {
                        "content": execution_result["response"],
                        "model_used": selected_model["id"],
                        "model_tier": selected_model.get("tier", "unknown"),
                        "task_type": analysis["task_type"],
                        "complexity_score": analysis["complexity_score"],
                        "complexity_level": analysis["complexity_level"],
                        "selection_reasoning": selected_model.get("reasoning", ""),
                        "estimated_cost": selected_model.get("estimated_cost", 0.0),
                        "response_time": execution_result["response_time"],
                        "confidence": execution_result.get("confidence", 0.0),
                        "cost_optimized": data.cost_optimization,
                        "fallback_models": selected_model.get("fallback_models", []),
                        "performance_metrics": {
                            "tokens_used": execution_result.get("tokens_used", 0),
                            "processing_time": processing_time,
                            "model_response_time": execution_result["response_time"]
                        }
                    }
                }
                
            except Exception as e:
                logger.error(f"Smart execution error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/promptcraft/models/available")
        @limiter.limit("100/minute") 
        async def get_available_models(
            request: Request,
            user_tier: Optional[str] = None,
            channel: str = "stable",
            include_metadata: bool = True,
            format: str = "ui"
        ):
            """
            Get available models filtered by user tier and channel.
            
            Returns models from either stable (verified) or experimental channels
            based on user permissions and preferences.
            """
            try:
                # Get models from appropriate channel
                models = await self._get_models_by_channel(channel, user_tier)
                
                # Format for UI or API consumption
                if format == "ui":
                    formatted_models = await self._format_models_for_ui(models)
                else:
                    formatted_models = models
                
                return {
                    "success": True,
                    "models": formatted_models,
                    "channel": channel,
                    "user_tier": user_tier,
                    "total_models": len(formatted_models),
                    "channels_available": ["stable", "experimental"],
                    "last_updated": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Model list error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/promptcraft/system/stats")
        async def get_system_stats():
            """Get system statistics and health metrics."""
            try:
                stats = self.data_manager.get_stats()
                
                # Add API server metrics
                stats["api_server"] = self.get_metrics()
                
                return {
                    "success": True,
                    "stats": stats
                }
                
            except Exception as e:
                logger.error(f"System stats error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _analyze_prompt_complexity(self, prompt: str, task_type_hint: Optional[str] = None) -> Dict[str, Any]:
        """Analyze prompt complexity using zen-mcp-server's complexity analyzer."""
        try:
            # Use the existing complexity analyzer
            analysis_result = self.complexity_analyzer.analyze(prompt)
            
            # Convert to expected format
            return {
                "task_type": analysis_result.task_type.value if hasattr(analysis_result.task_type, 'value') else str(analysis_result.task_type),
                "complexity_score": analysis_result.complexity_score,
                "complexity_level": analysis_result.complexity_level,
                "indicators": getattr(analysis_result, 'indicators', []),
                "reasoning": getattr(analysis_result, 'reasoning', f"Detected {analysis_result.task_type} task with {analysis_result.complexity_level} complexity")
            }
            
        except Exception as e:
            logger.error(f"Complexity analysis failed: {e}")
            # Fallback analysis
            return {
                "task_type": task_type_hint or "general",
                "complexity_score": 0.5,
                "complexity_level": "moderate",
                "indicators": [],
                "reasoning": "Fallback analysis due to complexity analyzer error"
            }
    
    async def _get_routing_recommendations(self, analysis: Dict[str, Any], user_tier: str) -> Dict[str, Any]:
        """Get model routing recommendations based on analysis and user tier."""
        try:
            # Map user tier to ModelLevel
            tier_mapping = {
                "free": ModelLevel.FREE,
                "limited": ModelLevel.FREE, 
                "full": ModelLevel.JUNIOR,
                "premium": ModelLevel.SENIOR,
                "admin": ModelLevel.EXECUTIVE
            }
            
            model_level = tier_mapping.get(user_tier, ModelLevel.FREE)
            
            # Get optimal model selection
            selected_model = self.model_router.select_optimal_model(
                complexity_score=analysis["complexity_score"],
                task_type=analysis["task_type"],
                user_level=model_level,
                cost_optimization=True
            )
            
            # Get alternative models
            alternatives = self.model_router.get_fallback_models(
                selected_model,
                max_alternatives=3
            )
            
            return {
                "primary": {
                    "model_id": selected_model.name,
                    "model_name": selected_model.display_name or selected_model.name,
                    "tier": selected_model.tier,
                    "reasoning": f"Selected for {analysis['task_type']} task with cost optimization"
                },
                "alternatives": [
                    {
                        "model_id": alt.name,
                        "model_name": alt.display_name or alt.name,
                        "tier": alt.tier
                    } for alt in alternatives
                ],
                "cost_comparison": {
                    "recommended_cost": selected_model.cost_per_token or 0.0,
                    "premium_alternative_cost": alternatives[0].cost_per_token if alternatives else 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"Routing recommendations failed: {e}")
            return {
                "primary": {
                    "model_id": "fallback-model",
                    "model_name": "Fallback Model", 
                    "tier": "free_champion",
                    "reasoning": "Fallback due to routing error"
                },
                "alternatives": [],
                "cost_comparison": {"recommended_cost": 0.0, "premium_alternative_cost": 0.0}
            }
    
    async def _select_optimal_model(self, analysis: Dict[str, Any], user_tier: str, channel: str, cost_optimization: bool) -> Dict[str, Any]:
        """Select optimal model for execution."""
        # Implementation similar to _get_routing_recommendations but focused on single best model
        recommendations = await self._get_routing_recommendations(analysis, user_tier)
        return recommendations["primary"]
    
    async def _execute_with_model(self, prompt: str, model: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute prompt with selected model."""
        # This would integrate with actual model execution
        # For now, return mock response
        start_time = time.time()
        
        # Simulate model execution time
        await asyncio.sleep(0.1)  # Mock execution delay
        
        response_time = time.time() - start_time
        
        return {
            "success": True,
            "response": f"Mock response from {model['model_id']} for prompt: {prompt[:50]}...",
            "response_time": response_time,
            "tokens_used": len(prompt) // 4,  # Rough token estimation
            "confidence": 0.85
        }
    
    async def _get_models_by_channel(self, channel: str, user_tier: Optional[str]) -> List[Dict[str, Any]]:
        """Get models filtered by channel and user tier."""
        from .data_manager import ModelChannel
        
        if channel == "experimental":
            models = self.data_manager.get_models_by_channel(ModelChannel.EXPERIMENTAL)
        else:
            models = self.data_manager.get_models_by_channel(ModelChannel.STABLE)
        
        # Filter by user tier if specified
        if user_tier:
            # Apply tier filtering logic here
            pass
        
        return models
    
    async def _format_models_for_ui(self, models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format models for UI display with enhanced information."""
        formatted = []
        
        for model in models:
            formatted_model = {
                "id": model.get("id", model.get("name", "unknown")),
                "display_name": self._generate_display_name(model),
                "name": model.get("name", "Unknown Model"),
                "tier": model.get("tier", "unknown"),
                "cost_per_token": model.get("cost_per_token", 0.0),
                "specialization": model.get("specialization", "general"),
                "humaneval_score": model.get("humaneval_score", 0.0),
                "context_window": model.get("context_window", 0),
                "provider": model.get("provider", "unknown"),
                "status": "active",
                "channel": "stable" if "experimental" not in model.get("id", "") else "experimental"
            }
            formatted.append(formatted_model)
        
        return formatted
    
    def _generate_display_name(self, model: Dict[str, Any]) -> str:
        """Generate enhanced display name for UI."""
        name = model.get("name", "Unknown")
        tier = model.get("tier", "")
        specialization = model.get("specialization", "")
        score = model.get("humaneval_score", 0.0)
        
        prefix = "🆓 " if model.get("cost_per_token", 0) == 0 else ""
        suffix = f" - {specialization.upper()}" if specialization != "general" else ""
        score_suffix = f" (Score: {score})" if score > 0 else ""
        
        return f"{prefix}⚡ {name}{suffix}{score_suffix}"
    
    def start_server(self, host: str = "0.0.0.0", port: int = 3000):
        """Start the FastAPI server."""
        try:
            config = uvicorn.Config(
                self.app,
                host=host,
                port=port,
                log_level="info",
                access_log=False  # We have our own request middleware
            )
            
            self.server = uvicorn.Server(config)
            self.running = True
            
            # Run server (this blocks)
            asyncio.run(self.server.serve())
            
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            self.running = False
    
    def stop_server(self):
        """Stop the FastAPI server gracefully."""
        if self.server:
            self.server.should_exit = True
        self.running = False
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self.running
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get API server performance metrics."""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0.0
        )
        
        success_rate = (
            self.successful_requests / self.request_count 
            if self.request_count > 0 else 0.0
        )
        
        return {
            "total_requests": self.request_count,
            "successful_requests": self.successful_requests,
            "success_rate": success_rate,
            "average_response_time": avg_response_time,
            "uptime": time.time() - getattr(self, '_start_time', time.time())
        }