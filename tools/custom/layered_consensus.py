"""
Layered Consensus Custom Tool - Organizational hierarchy with layered model selection

Implements the layered approach where higher tiers include all lower-tier analysis:
- Junior: 3 free models for basic roles
- Senior: 3 free + 3 value models for basic + professional roles  
- Executive: 3 free + 3 value + 2 premium models for comprehensive analysis

This approach is more cost-effective and organizationally realistic.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import Field

from mcp.types import TextContent
from tools.shared.base_tool import BaseTool
from tools.shared.base_models import ToolRequest

logger = logging.getLogger(__name__)

# Dynamic model selection with layered approach
from .dynamic_model_selector import get_model_selector


class LayeredConsensusRequest(ToolRequest):
    """Request for layered consensus analysis"""
    
    proposal: str = Field(..., description="The question or proposal to analyze via layered consensus")
    org_level: str = Field(default="senior", description="Organizational level: junior, senior, or executive")


class LayeredConsensusTool(BaseTool):
    """
    Layered organizational consensus analysis.
    
    Uses incremental model selection where higher tiers build on lower tiers:
    - Junior (3 models): Basic roles with free models
    - Senior (6 models): Basic + professional roles with free + value models
    - Executive (8 models): Basic + professional + strategic with free + value + premium
    
    This approach is cost-efficient and mirrors real IT organizational structures.
    """
    
    def get_name(self) -> str:
        return "layered_consensus"
    
    def get_description(self) -> str:
        return (
            "LAYERED ORGANIZATIONAL CONSENSUS - Cost-efficient layered approach where higher tiers "
            "build on lower-tier analysis. Junior uses free models for basic roles, Senior adds "
            "professional analysis, Executive adds strategic perspective. Mirrors real IT hierarchy "
            "and optimizes cost by using appropriate models for each role level."
        )
    
    def get_request_model(self):
        return LayeredConsensusRequest
    
    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute layered consensus analysis"""
        
        try:
            # Convert dict arguments to Pydantic model
            request = LayeredConsensusRequest(**arguments)
            
            # Select models using layered approach
            layered_models, total_cost = self._select_layered_models(request.org_level)
            
            # Create role assignments for layered models
            model_assignments = self._create_layered_assignments(layered_models)
            
            # Execute zen consensus tool with layered assignments
            return await self._execute_zen_consensus(request.proposal, model_assignments, request.org_level, total_cost)
            
        except Exception as e:
            logger.exception(f"Layered consensus execution failed: {e}")
            error_response = {
                "status": "error", 
                "message": f"Layered consensus analysis failed: {str(e)}",
                "tool": "layered_consensus"
            }
            return [TextContent(type="text", text=str(error_response))]
    
    def _select_layered_models(self, org_level: str) -> tuple[dict[str, list[str]], float]:
        """Select models using layered organizational approach with rate limit fallback"""
        
        selector = get_model_selector()
        
        try:
            # First try the layered selection approach
            layered_models, total_cost = selector.select_layered_consensus_models(org_level)
            
            # Validate minimum models available
            total_models = sum(len(models) for models in layered_models.values())
            min_required = {"junior": 2, "senior": 4, "executive": 6}  # Reduced minimums for reliability
            
            if total_models >= min_required.get(org_level.lower(), 2):
                logger.info(f"Layered {org_level} selection complete: {total_models} models")
                return layered_models, total_cost
            
            # If layered approach doesn't have enough models, try fallback
            logger.warning(f"Layered selection insufficient ({total_models} models), trying fallback selection")
            
            # Use fallback-aware selection and convert to layered format
            fallback_models, fallback_cost = selector.select_models_with_fallback(org_level, "layered_consensus")
            
            # Convert flat list to layered format for compatibility
            layered_fallback = self._convert_to_layered_format(fallback_models, org_level)
            
            logger.info(f"Fallback layered selection: {len(fallback_models)} models")
            return layered_fallback, fallback_cost
            
        except Exception as e:
            logger.error(f"Layered model selection failed: {e}")
            # Emergency fallback - create minimal layered structure
            emergency_models = ["gpt-4o-mini", "claude-3-5-haiku"]  # Known stable models
            emergency_layered = self._convert_to_layered_format(emergency_models, "junior")
            logger.error("Using emergency layered fallback")
            return emergency_layered, 1.0
    
    def _convert_to_layered_format(self, model_list: list[str], org_level: str) -> dict[str, list[str]]:
        """Convert flat model list to layered format for compatibility"""
        layered = {"junior": []}
        
        # Distribute models across tiers based on org level
        if org_level.lower() == "junior":
            layered["junior"] = model_list
        elif org_level.lower() == "senior":
            # Split between junior and senior
            mid_point = len(model_list) // 2
            layered["junior"] = model_list[:mid_point] if model_list else []
            layered["senior"] = model_list[mid_point:] if model_list else []
        else:  # executive
            # Split across all three tiers
            third = len(model_list) // 3
            layered["junior"] = model_list[:third] if model_list else []
            layered["senior"] = model_list[third:2*third] if len(model_list) > third else []
            layered["executive"] = model_list[2*third:] if len(model_list) > 2*third else []
        
        return layered
    
    def _create_layered_assignments(self, layered_models: dict[str, list[str]]) -> list[dict]:
        """Create role assignments for layered models"""
        
        selector = get_model_selector()
        assignments = selector.create_layered_role_assignments(layered_models)
        
        logger.info(f"Created {len(assignments)} layered role assignments")
        
        return assignments
    
    async def _execute_zen_consensus(self, proposal: str, model_assignments: list[dict], org_level: str, estimated_cost: float) -> list[TextContent]:
        """Execute zen consensus tool with layered configuration"""
        
        try:
            from tools.consensus import ConsensusTool
            
            consensus_tool = ConsensusTool()
            
            consensus_args = {
                "step": proposal,
                "step_number": 1,
                "total_steps": len(model_assignments),
                "next_step_required": False,
                "findings": f"Automated {org_level} layered consensus analysis requested",
                "models": model_assignments,
                "model": "anthropic/claude-sonnet-4",
                "current_model_index": 0
            }
            
            result = await consensus_tool.execute_workflow(consensus_args)
            
            # Add layered organization metadata
            model_breakdown = self._analyze_model_breakdown(model_assignments)
            automation_info = f"""LAYERED CONSENSUS COMPLETE

Organizational Approach: Layered {org_level.title()} Level Analysis
Total Models: {len(model_assignments)} models across organizational tiers
Model Breakdown: {model_breakdown}
Estimated Cost: ${estimated_cost:.2f}
Architecture: Cost-efficient layered approach (basic → professional → strategic)
Tool: layered_consensus

"""
            
            if result and len(result) > 0:
                existing_content = result[0].text if hasattr(result[0], 'text') else str(result[0])
                enhanced_content = automation_info + existing_content
                result[0] = TextContent(type="text", text=enhanced_content)
            
            return result
            
        except Exception as e:
            logger.exception(f"Zen consensus execution failed: {e}")
            raise RuntimeError(f"Failed to execute layered consensus: {str(e)}")
    
    def _analyze_model_breakdown(self, assignments: list[dict]) -> str:
        """Analyze and describe the model tier breakdown"""
        
        # This is a simplified breakdown - could be enhanced with actual tier analysis
        total = len(assignments)
        if total <= 3:
            return f"{total} junior-level models (basic analysis)"
        elif total <= 6:
            return f"~3 junior + ~3 senior models (basic + professional)"
        else:
            return f"~3 junior + ~3 senior + ~2 executive models (comprehensive layered)"
    
    def _is_model_available(self, model_name: str) -> bool:
        """Check if model is available"""
        try:
            provider = self.get_model_provider(model_name)
            return provider is not None
        except:
            return False
    
    async def prepare_prompt(self, request: LayeredConsensusRequest) -> str:
        """Not used - uses execute() directly"""
        return ""
    
    def get_system_prompt(self) -> str:
        """System prompt for layered consensus analysis"""
        return "You are performing layered organizational consensus analysis using multiple models across different organizational levels."
    
    def get_input_schema(self) -> dict:
        """Input schema for layered consensus tool"""
        return {
            "type": "object",
            "properties": {
                "proposal": {
                    "type": "string",
                    "description": "The question or proposal to analyze via layered consensus"
                },
                "org_level": {
                    "type": "string", 
                    "enum": ["junior", "senior", "executive"],
                    "default": "senior",
                    "description": "Organizational level: junior, senior, or executive"
                }
            },
            "required": ["proposal"]
        }