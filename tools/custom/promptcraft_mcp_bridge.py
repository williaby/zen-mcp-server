"""
PromptCraft MCP Bridge - Custom Tool for MCP Stdio Integration

This tool provides a bridge between PromptCraft's MCP client and zen-mcp-server's internal tools.
It exposes all PromptCraft operations as native MCP functions while maintaining compatibility
with the existing HTTP API.

Architecture:
- Bridge pattern: Translates MCP calls to internal tool calls
- Action-based routing: Single tool with multiple actions
- Zero conflicts: Uses plugin-style custom tool architecture
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from pydantic import BaseModel, Field
from mcp.types import TextContent

from tools.shared.base_models import ToolRequest
from tools.simple.base import SimpleTool

# Import internal tools that we'll bridge to
from tools.chat import ChatTool
from tools.listmodels import ListModelsTool
from tools.custom.dynamic_model_selector import DynamicModelSelectorTool

logger = logging.getLogger(__name__)


class PromptCraftMCPBridgeRequest(ToolRequest):
    """Request model for PromptCraft MCP Bridge operations."""

    action: str = Field(
        ..., 
        description="Action to perform: 'analyze_route', 'smart_execute', 'list_models'",
        enum=["analyze_route", "smart_execute", "list_models"]
    )
    
    # Common fields
    prompt: Optional[str] = Field(None, description="The prompt to analyze or execute")
    user_tier: Optional[str] = Field(None, description="User tier: free|limited|full|premium|admin")
    
    # Route analysis specific
    task_type: Optional[str] = Field(None, description="Optional task type hint for route analysis")
    
    # Smart execution specific
    channel: Optional[str] = Field("stable", description="Model channel: stable|experimental")
    cost_optimization: Optional[bool] = Field(True, description="Enable cost optimization")
    include_reasoning: Optional[bool] = Field(True, description="Include reasoning in response")
    
    # Model listing specific
    include_metadata: Optional[bool] = Field(True, description="Include detailed metadata")
    format: Optional[str] = Field("ui", description="Response format: ui|api")


class PromptCraftMCPBridgeTool(SimpleTool):
    """
    MCP Bridge tool for PromptCraft integration.
    
    This tool acts as a bridge between PromptCraft's MCP client and zen-mcp-server's
    internal tools, providing a native MCP interface for all PromptCraft operations.
    """

    def __init__(self):
        super().__init__()
        # Initialize internal tools that we'll bridge to
        self.chat_tool = ChatTool()
        self.listmodels_tool = ListModelsTool()
        self.dynamic_model_selector_tool = DynamicModelSelectorTool()
        
        logger.info("✅ PromptCraft MCP Bridge initialized")

    def get_name(self) -> str:
        return "promptcraft_mcp_bridge"

    def get_description(self) -> str:
        return (
            "PromptCraft MCP Bridge - Provides native MCP access to PromptCraft functionality. "
            "Supports route analysis, smart execution, and model listing operations."
        )

    def get_tool_fields(self) -> Dict[str, Any]:
        """Return tool-specific field definitions for clean MCP interface."""
        return {
            "action": {
                "type": "string",
                "description": "Action to perform: 'analyze_route', 'smart_execute', 'list_models'",
                "enum": ["analyze_route", "smart_execute", "list_models"],
            },
            "prompt": {
                "type": "string",
                "description": "The prompt to analyze or execute",
            },
            "user_tier": {
                "type": "string", 
                "description": "User tier: free|limited|full|premium|admin",
                "enum": ["free", "limited", "full", "premium", "admin"],
            },
            "task_type": {
                "type": "string",
                "description": "Optional task type hint for route analysis",
            },
            "channel": {
                "type": "string",
                "default": "stable",
                "description": "Model channel: stable|experimental",
                "enum": ["stable", "experimental"],
            },
            "cost_optimization": {
                "type": "boolean",
                "default": True,
                "description": "Enable cost optimization",
            },
            "include_reasoning": {
                "type": "boolean", 
                "default": True,
                "description": "Include reasoning in response",
            },
            "include_metadata": {
                "type": "boolean",
                "default": True,
                "description": "Include detailed metadata",
            },
            "format": {
                "type": "string",
                "default": "ui",
                "description": "Response format: ui|api",
                "enum": ["ui", "api"],
            },
        }

    def get_required_fields(self) -> List[str]:
        """Return list of required field names."""
        return ["action"]

    def get_system_prompt(self) -> str:
        return """You are the PromptCraft MCP Bridge, providing native MCP access to PromptCraft functionality.

Your role is to:
1. Route analysis - Analyze prompts and provide model recommendations
2. Smart execution - Execute prompts with optimal model routing
3. Model listing - Provide available models for user tiers

You bridge between MCP protocol and internal zen-mcp-server tools while maintaining
compatibility with the existing HTTP API. Always provide comprehensive, actionable responses."""

    async def _call_internal_tool(self, tool, method_name: str, *args, **kwargs) -> Any:
        """Helper to call internal tool methods safely."""
        try:
            method = getattr(tool, method_name)
            if asyncio.iscoroutinefunction(method):
                return await method(*args, **kwargs)
            else:
                return method(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error calling {tool.__class__.__name__}.{method_name}: {e}")
            raise

    async def _analyze_route_action(self, request: PromptCraftMCPBridgeRequest) -> Dict[str, Any]:
        """Handle route analysis action."""
        if not request.prompt:
            raise ValueError("Prompt is required for route analysis")
            
        start_time = time.time()
        
        # Use dynamic model selector for route analysis  
        selector_request = {
            "requirements": request.prompt,
            "task_type": request.task_type or "general", 
            "complexity_level": "medium",  # Default complexity
            "budget_preference": "balanced",
            "num_models": 3,
            "model": "flash",  # Use fast model for analysis
        }
        
        try:
            # Call the dynamic model selector tool
            analysis_result = await self._call_internal_tool(
                self.dynamic_model_selector_tool, 
                "execute", 
                selector_request
            )
            
            processing_time = time.time() - start_time
            
            # Extract analysis from the model selector response
            analysis_content = analysis_result.get("content", "") if isinstance(analysis_result, dict) else str(analysis_result)
            
            return {
                "success": True,
                "analysis": {
                    "task_type": request.task_type or "general",
                    "complexity_score": 0.5,  # Default score
                    "complexity_level": "medium",
                    "indicators": ["mcp_bridge_analysis"],
                    "reasoning": analysis_content,
                },
                "recommendations": {
                    "primary_model": "claude-3-5-sonnet-20241022",
                    "alternative_models": ["gpt-4o", "claude-3-opus-20240229"],
                    "estimated_cost": 0.01,
                    "confidence": 0.85,
                },
                "processing_time": processing_time,
                "bridge_version": "1.0.0",
            }
            
        except Exception as e:
            logger.error(f"Route analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
            }

    async def _smart_execute_action(self, request: PromptCraftMCPBridgeRequest) -> Dict[str, Any]:
        """Handle smart execution action."""
        if not request.prompt:
            raise ValueError("Prompt is required for smart execution")
            
        start_time = time.time()
        
        # Use chat tool for execution with model routing
        chat_request = {
            "prompt": request.prompt,
            "model": "auto",  # Let the router decide
            "temperature": 0.7,
            "thinking_mode": "medium",
            "use_websearch": True,
        }
        
        try:
            # Call the chat tool for execution
            execution_result = await self._call_internal_tool(
                self.chat_tool,
                "execute", 
                chat_request
            )
            
            processing_time = time.time() - start_time
            
            # Extract content from chat response
            if isinstance(execution_result, dict):
                content = execution_result.get("content", "")
                model_used = execution_result.get("metadata", {}).get("model", "unknown")
            else:
                content = str(execution_result)
                model_used = "unknown"
            
            return {
                "success": True,
                "response": {
                    "content": content,
                    "model_used": model_used,
                    "reasoning": "Executed via MCP bridge with smart routing" if request.include_reasoning else None,
                },
                "execution_metadata": {
                    "channel": request.channel,
                    "cost_optimization": request.cost_optimization,
                    "processing_time": processing_time,
                },
                "bridge_version": "1.0.0",
            }
            
        except Exception as e:
            logger.error(f"Smart execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
            }

    async def _list_models_action(self, request: PromptCraftMCPBridgeRequest) -> Dict[str, Any]:
        """Handle model listing action."""
        start_time = time.time()
        
        try:
            # Call the listmodels tool
            models_result = await self._call_internal_tool(
                self.listmodels_tool,
                "execute",
                {"model": "flash"}  # Use fast model for listing
            )
            
            processing_time = time.time() - start_time
            
            # Process the models list based on user tier and format
            if isinstance(models_result, dict):
                models_content = models_result.get("content", "")
            else:
                models_content = str(models_result)
            
            # Basic model filtering based on tier (simplified for bridge)
            available_models = []
            if request.user_tier in ["full", "premium", "admin"]:
                available_models = ["claude-3-5-sonnet-20241022", "gpt-4o", "claude-3-opus-20240229", "gemini-2.0-flash-exp"]
            elif request.user_tier in ["limited"]:
                available_models = ["claude-3-5-haiku-20241022", "gpt-4o-mini", "gemini-1.5-flash"]
            else:  # free tier
                available_models = ["llama-3.3-70b-instruct:free", "qwen-2.5-coder-32b-instruct:free"]
            
            models_data = []
            for model in available_models:
                models_data.append({
                    "id": model,
                    "name": model.replace("-", " ").title(),
                    "provider": model.split("-")[0] if "-" in model else "unknown",
                    "tier": request.user_tier or "free",
                    "channel": request.channel,
                    "available": True,
                })
            
            return {
                "success": True,
                "models": models_data,
                "metadata": {
                    "user_tier": request.user_tier,
                    "channel": request.channel,
                    "format": request.format,
                    "total_models": len(models_data),
                    "include_metadata": request.include_metadata,
                } if request.include_metadata else {},
                "processing_time": processing_time,
                "bridge_version": "1.0.0",
                "raw_models_content": models_content if request.format == "api" else None,
            }
            
        except Exception as e:
            logger.error(f"Model listing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
            }

    async def execute(self, request: Union[Dict[str, Any], PromptCraftMCPBridgeRequest]) -> List[TextContent]:
        """Execute the PromptCraft MCP bridge operation."""
        # Handle both dict and Pydantic model inputs
        if isinstance(request, dict):
            request = PromptCraftMCPBridgeRequest(**request)
        
        logger.info(f"🌉 PromptCraft MCP Bridge executing action: {request.action}")
        
        try:
            # Route to appropriate action handler
            if request.action == "analyze_route":
                result = await self._analyze_route_action(request)
            elif request.action == "smart_execute":
                result = await self._smart_execute_action(request)
            elif request.action == "list_models":
                result = await self._list_models_action(request)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown action: {request.action}",
                    "available_actions": ["analyze_route", "smart_execute", "list_models"],
                }
            
            # Add bridge metadata
            result.update({
                "bridge_timestamp": datetime.now().isoformat(),
                "bridge_action": request.action,
                "mcp_integration": True,
            })
            
            return [TextContent(
                type="text", 
                text=f"PromptCraft MCP Bridge Result:\n\n{self._format_result_as_json(result)}"
            )]
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "action": request.action,
                "bridge_timestamp": datetime.now().isoformat(),
            }
            logger.error(f"❌ PromptCraft MCP Bridge error: {e}")
            return [TextContent(
                type="text",
                text=f"PromptCraft MCP Bridge Error:\n\n{self._format_result_as_json(error_result)}"
            )]

    def _format_result_as_json(self, result: Dict[str, Any]) -> str:
        """Format result as pretty JSON for better readability."""
        import json
        try:
            return json.dumps(result, indent=2, default=str)
        except Exception:
            return str(result)

    def get_request_model(self):
        """Return the request model for this tool."""
        return PromptCraftMCPBridgeRequest