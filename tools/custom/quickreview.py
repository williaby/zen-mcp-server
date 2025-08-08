"""
QuickReview Custom Tool - Basic validation using free models only

This is a completely self-contained custom tool that provides quick validation
of code, documentation, and basic logic using 2-3 free models with simple 
role-based analysis. Designed for fast, zero-cost basic validation tasks.

This tool is isolated in tools/custom/ to minimize merge conflicts and 
enable independent development of custom functionality.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from pydantic import Field

if TYPE_CHECKING:
    from tools.models import ToolModelCategory

from mcp.types import TextContent

from config import TEMPERATURE_ANALYTICAL
from tools.shared.base_models import WorkflowRequest
from tools.workflow.base import WorkflowTool

logger = logging.getLogger(__name__)

# Free models from current configuration (cost = $0)
# This list is updated based on /docs/current_models.md
FREE_MODELS = [
    "deepseek/deepseek-r1-distill-llama-70b:free",  # Best free reasoning
    "meta-llama/llama-3.1-405b-instruct:free",      # Largest free model (80.5% HumanEval)
    "qwen/qwen-2.5-coder-32b-instruct:free",        # Free coding specialist
    "meta-llama/llama-4-maverick:free",             # Latest Meta architecture
    "meta-llama/llama-3.3-70b-instruct:free",       # Efficient 70B performance
    "qwen/qwen2.5-vl-72b-instruct:free",           # Vision-language capabilities
    "microsoft/phi-4-reasoning:free",               # Debugging specialist
    "qwen/qwq-32b:free",                            # Free reasoning model
    "moonshotai/kimi-k2:free",                      # Alternative provider
]

# Priority order for selection (best free models first)
FREE_MODEL_PRIORITY = [
    "deepseek/deepseek-r1-distill-llama-70b:free",  # Best free reasoning
    "meta-llama/llama-3.1-405b-instruct:free",      # Largest free model
    "qwen/qwen-2.5-coder-32b-instruct:free",        # Free coding specialist
]

# Simple role definitions for basic validation
QUICKREVIEW_ROLES = {
    "syntax_checker": "Focus on basic syntax, grammar, formatting, and obvious errors",
    "logic_reviewer": "Review basic logic flow, consistency, and simple correctness issues", 
    "docs_checker": "Evaluate documentation clarity, completeness, and accuracy"
}

# Self-contained system prompt (no external prompt file needed)
QUICKREVIEW_SYSTEM_PROMPT = """You are an AI assistant performing quick basic validation using free models.

Your goal is to provide helpful, accurate feedback for basic validation tasks such as:
- Syntax and grammar checking
- Basic code validation and logic review
- Documentation clarity and completeness assessment
- Simple formatting and style consistency checks

VALIDATION APPROACH:
- Be practical and constructive in your analysis
- Focus on clear, obvious issues that can be identified reliably
- Provide specific, actionable recommendations when possible
- Acknowledge limitations of basic validation scope
- Highlight issues that may require more thorough analysis

FEEDBACK STRUCTURE:
1. **Summary**: Brief overview of validation findings
2. **Specific Issues**: List clear problems found with locations/examples
3. **Recommendations**: Concrete suggestions for improvement
4. **Scope Notes**: Mention any limitations or areas needing deeper analysis

GUIDELINES:
- Stay within the scope of basic validation - don't overreach into complex analysis
- Be clear and direct about issues found
- Provide constructive suggestions, not just criticism
- Use examples from the content when highlighting issues
- Maintain a helpful, professional tone
- If the content is generally good, acknowledge that while noting minor improvements

Remember: You're performing basic validation suitable for free model capabilities. 
Focus on being accurate and helpful within this scope rather than attempting 
complex analysis that requires premium models."""

# Tool-specific field descriptions
QUICKREVIEW_FIELD_DESCRIPTIONS = {
    "proposal": (
        "What to review or validate. Be specific about what you want checked. "
        "Examples: 'Check this code syntax', 'Review documentation clarity', "
        "'Validate basic logic flow in this function'"
    ),
    "focus": (
        "Optional focus area for validation. Choose from: 'syntax' (grammar, formatting, errors), "
        "'logic' (basic logic flow and consistency), 'docs' (documentation clarity), "
        "'general' (overall basic validation). Defaults to 'general'."
    ),
}


class QuickReviewRequest(WorkflowRequest):
    """Request model for QuickReview workflow steps"""

    # Core parameters - these will be shown to users
    proposal: str = Field(..., description=QUICKREVIEW_FIELD_DESCRIPTIONS["proposal"])
    focus: str | None = Field(
        default="general", 
        description=QUICKREVIEW_FIELD_DESCRIPTIONS["focus"]
    )
    
    # Override for quick reviews - shown to users
    temperature: float | None = Field(default=TEMPERATURE_ANALYTICAL)
    thinking_mode: str | None = Field(default="low")  # Low thinking for speed
    
    # Hide complex workflow fields from MCP schema - these are managed internally
    files_checked: list[str] | None = Field(default_factory=list, exclude=True)
    relevant_context: list[str] | None = Field(default_factory=list, exclude=True) 
    issues_found: list[dict] | None = Field(default_factory=list, exclude=True)
    hypothesis: str | None = Field(None, exclude=True)
    backtrack_from_step: int | None = Field(None, exclude=True)
    confidence: str | None = Field(default="low", exclude=True)
    use_websearch: bool | None = Field(default=True, exclude=True)
    

class QuickReviewTool(WorkflowTool):
    """
    Quick validation tool using free models only.
    
    This custom tool provides fast, zero-cost basic validation using 2-3 free models 
    with simple role-based analysis. Ideal for syntax checking, documentation
    review, and basic logic validation.
    
    Features:
    - Uses only free models (cost = $0)
    - Dynamic model selection with availability handling
    - Role-based analysis (syntax, logic, documentation)
    - 3-step workflow optimized for speed
    - Completely self-contained to avoid merge conflicts
    """

    def __init__(self):
        super().__init__()
        self.selected_models = []
        self.model_roles = {}

    def get_name(self) -> str:
        return "quickreview"

    def get_description(self) -> str:
        return (
            "QUICK VALIDATION - Basic validation using free models only (2-3 models, $0 cost). "
            "Perfect for: grammar and syntax checking, basic code validation, documentation review, "
            "simple logic verification. Uses only free models with simple role-based analysis for "
            "fast, zero-cost validation. Ideal when you need quick feedback without premium model costs."
        )

    def get_system_prompt(self) -> str:
        return QUICKREVIEW_SYSTEM_PROMPT

    def get_default_temperature(self) -> float:
        return TEMPERATURE_ANALYTICAL

    def get_model_category(self) -> ToolModelCategory:
        """Quick review prioritizes speed and cost efficiency (free models)"""
        from tools.models import ToolModelCategory
        return ToolModelCategory.FAST_RESPONSE

    def get_workflow_request_model(self):
        """Return the quickreview workflow-specific request model."""
        return QuickReviewRequest

    def get_input_schema(self) -> dict[str, Any]:
        """Generate clean input schema for quickreview with minimal parameters."""
        from tools.workflow.schema_builders import WorkflowSchemaBuilder
        
        # QuickReview tool-specific field definitions - only show essential fields
        quickreview_field_overrides = {
            "proposal": {
                "type": "string",
                "description": QUICKREVIEW_FIELD_DESCRIPTIONS["proposal"],
            },
            "focus": {
                "type": "string", 
                "enum": ["syntax", "logic", "docs", "general"],
                "default": "general",
                "description": QUICKREVIEW_FIELD_DESCRIPTIONS["focus"],
            },
        }

        # Define excluded fields for quickreview workflow - hide advanced internal fields
        excluded_workflow_fields = [
            "files_checked",         # Managed internally
            "relevant_context",      # Managed internally  
            "issues_found",          # Managed internally
            "hypothesis",            # Not used in basic validation
            "backtrack_from_step",   # Not used in simple workflow
            "confidence",            # Managed internally
            "use_assistant_model",   # Not used - quickreview is self-contained
        ]
        
        # Hide advanced common fields for simpler interface
        excluded_common_fields = [
            "use_websearch",         # Always enabled by default
        ]

        return WorkflowSchemaBuilder.build_schema(
            tool_specific_fields=quickreview_field_overrides,
            required_fields=["proposal"],  # Only proposal is required from user
            excluded_workflow_fields=excluded_workflow_fields,
            excluded_common_fields=excluded_common_fields,
            tool_name=self.get_name(),
        )

    def get_required_fields(self) -> list[str]:
        """Proposal is required beyond standard workflow fields."""
        return ["proposal"]

    def get_required_actions(
        self, step_number: int, confidence: str, findings: str, total_steps: int
    ) -> list[str]:
        """Define required actions for each quickreview phase."""
        if step_number == 1:
            return [
                "Analyze the request and identify what needs validation",
                "If files provided, examine relevant sections for validation",
                "Prepare for consultation with free models for basic validation",
            ]
        elif step_number == 2:
            return [
                "Review free model responses for basic validation feedback",
                "Identify common themes and clear issues across responses", 
                "Prepare synthesis of validation findings",
            ]
        else:
            return [
                "Complete synthesis of all free model validation feedback",
                "Provide clear, actionable recommendations within scope of basic validation",
                "Highlight any issues requiring more thorough analysis",
            ]

    def should_call_expert_analysis(self, consolidated_findings) -> bool:
        """QuickReview completes with its own free model consultations."""
        return False  # No external expert analysis needed

    def prepare_expert_analysis_context(self, consolidated_findings) -> str:
        """Not used - quickreview handles analysis internally."""
        return ""

    def requires_expert_analysis(self) -> bool:
        """QuickReview is self-contained."""
        return False

    async def execute_workflow(self, arguments: dict[str, Any]) -> list:
        """Execute quickreview workflow with free model consultations."""
        
        # Validate request
        request = self.get_workflow_request_model()(**arguments)
        
        # On first step, select free models and assign roles
        if request.step_number == 1:
            self.selected_models = self._select_free_models(request.focus)
            self.model_roles = self._assign_roles_to_models(self.selected_models, request.focus)
            
            # Set total steps based on workflow: analysis + consultation + synthesis
            request.total_steps = 3

        # Handle different steps
        if request.step_number == 1:
            # Step 1: Initial analysis + first model consultation
            return await self._handle_initial_analysis(request)
        elif request.step_number == 2:
            # Step 2: Continue model consultations
            return await self._handle_model_consultations(request)
        else:
            # Step 3: Final synthesis
            return await self._handle_final_synthesis(request)

    async def _handle_initial_analysis(self, request) -> list:
        """Handle initial analysis and first model consultation."""
        
        # Consult first free model
        first_model = self.selected_models[0] if self.selected_models else None
        model_response = None
        
        if first_model:
            model_response = await self._consult_free_model(first_model, request)
        
        response_data = {
            "status": "quickreview_started",
            "step_number": 1,
            "total_steps": 3,
            "next_step_required": True,
            "models_selected": self.selected_models,
            "model_roles": self.model_roles,
            "cost_estimate": "$0.00 (free models only)",
        }
        
        if model_response:
            response_data["first_model_response"] = model_response
            response_data["next_steps"] = (
                f"Initial analysis complete. {model_response['model']} provided {model_response['role']} feedback. "
                f"Continue with step 2 to get remaining model consultations."
            )
        else:
            response_data["next_steps"] = (
                "Initial analysis complete. Continue with step 2 for model consultations."
            )

        # Add standard metadata
        response_data["metadata"] = {
            "tool_name": self.get_name(),
            "workflow_type": "free_model_validation",
            "cost": "$0.00",
            "custom_tool": True,  # Mark as custom tool
        }

        return [TextContent(type="text", text=json.dumps(response_data, indent=2, ensure_ascii=False))]

    async def _handle_model_consultations(self, request) -> list:
        """Handle remaining model consultations."""
        
        model_responses = []
        
        # Consult remaining models (skip first one already done in step 1)
        for model in self.selected_models[1:]:
            model_response = await self._consult_free_model(model, request)
            if model_response:
                model_responses.append(model_response)

        response_data = {
            "status": "model_consultations_complete",
            "step_number": 2,
            "total_steps": 3,
            "next_step_required": True,
            "model_responses": model_responses,
            "next_steps": (
                f"Consulted {len(model_responses)} additional free models. "
                "Proceed to step 3 for final synthesis of all validation feedback."
            ),
        }

        return [TextContent(type="text", text=json.dumps(response_data, indent=2, ensure_ascii=False))]

    async def _handle_final_synthesis(self, request) -> list:
        """Handle final synthesis of all model responses."""
        
        response_data = {
            "status": "quickreview_complete", 
            "step_number": 3,
            "total_steps": 3,
            "next_step_required": False,
            "validation_complete": True,
            "models_consulted": len(self.selected_models),
            "total_cost": "$0.00",
            "next_steps": (
                "QUICKREVIEW COMPLETE. All free models have provided validation feedback. "
                "Synthesize the findings and present clear, actionable recommendations based on "
                "the validation results from the free model consultations."
            ),
        }

        return [TextContent(type="text", text=json.dumps(response_data, indent=2, ensure_ascii=False))]

    async def _consult_free_model(self, model_name: str, request) -> dict:
        """Consult a single free model for validation feedback."""
        try:
            # Get the provider for this model
            provider = self.get_model_provider(model_name)
            
            # Get role for this model
            role = self.model_roles.get(model_name, "general_validator")
            role_description = QUICKREVIEW_ROLES.get(role, "Provide general validation feedback")
            
            # Prepare prompt
            prompt = self._prepare_validation_prompt(request, role_description)
            
            # Add file content if provided
            if hasattr(request, 'relevant_files') and request.relevant_files:
                file_content, _ = self._prepare_file_content_for_prompt(
                    request.relevant_files,
                    getattr(request, 'continuation_id', None),
                    "Context files for validation",
                )
                if file_content:
                    prompt = f"{prompt}\n\n=== FILES TO VALIDATE ===\n{file_content}\n=== END FILES ==="

            # Call the model with validation-specific system prompt
            system_prompt = f"{self.get_system_prompt()}\n\nROLE: {role_description}"
            
            response = provider.generate_content(
                prompt=prompt,
                model_name=model_name,
                system_prompt=system_prompt,
                temperature=0.2,  # Low temperature for consistent validation
                thinking_mode="low",  # Quick thinking for fast results
            )

            return {
                "model": model_name,
                "role": role,
                "status": "success",
                "feedback": response.content,
                "metadata": {
                    "provider": provider.get_provider_type().value,
                    "cost": "$0.00",
                },
            }

        except Exception as e:
            logger.exception("Error consulting free model %s", model_name)
            return {
                "model": model_name,
                "role": self.model_roles.get(model_name, "unknown"),
                "status": "error",
                "error": str(e),
            }

    def _select_free_models(self, focus: str | None = None) -> list[str]:
        """
        Select 2-3 best available free models for validation.
        
        Uses dynamic availability checking to handle free model outages.
        Falls back through priority list and full free model list.
        """
        
        selected = []
        
        # First, try priority models in order
        logger.info("Attempting to select free models from priority list...")
        for model in FREE_MODEL_PRIORITY:
            if self._is_model_available(model):
                selected.append(model)
                logger.info(f"✅ Selected priority model: {model}")
                if len(selected) >= 3:  # Limit to 3 models max
                    break
            else:
                logger.info(f"❌ Priority model unavailable: {model}")
        
        # If we don't have enough models, try others from the full free list
        if len(selected) < 2:
            logger.info(f"Need more models (have {len(selected)}), trying full free model list...")
            for model in FREE_MODELS:
                if model not in selected and self._is_model_available(model):
                    selected.append(model)
                    logger.info(f"✅ Selected fallback model: {model}")
                    if len(selected) >= 3:
                        break
        
        # Final validation - ensure we have at least 1 model
        if len(selected) == 0:
            error_msg = (
                "No free models are currently available. This may be a temporary issue. "
                "Try again in a few minutes or check model availability with the listmodels tool."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        if len(selected) < 2:
            logger.warning(f"Only {len(selected)} free model(s) available, proceeding with reduced capacity")
        
        logger.info(f"Final selection: {len(selected)} free models: {selected}")
        return selected

    def _is_model_available(self, model_name: str) -> bool:
        """
        Check if a specific model is currently available.
        
        Uses robust availability checking that handles provider outages.
        """
        try:
            # Try to get provider for the model
            provider = self.get_model_provider(model_name)
            if not provider:
                return False
            
            # Additional availability check could go here if providers support it
            # For now, if we can resolve the provider, assume model is available
            return True
            
        except Exception as e:
            logger.debug(f"Model {model_name} availability check failed: {e}")
            return False

    def _assign_roles_to_models(self, models: list[str], focus: str | None = None) -> dict[str, str]:
        """Assign validation roles to selected models."""
        
        if not models:
            return {}
        
        roles = list(QUICKREVIEW_ROLES.keys())
        model_roles = {}
        
        # If focus specified, prioritize that role
        if focus and focus in QUICKREVIEW_ROLES:
            model_roles[models[0]] = focus
            remaining_roles = [r for r in roles if r != focus]
            remaining_models = models[1:]
        else:
            remaining_roles = roles
            remaining_models = models
        
        # Assign remaining roles
        for i, model in enumerate(remaining_models):
            if i < len(remaining_roles):
                model_roles[model] = remaining_roles[i]
            else:
                # If more models than roles, assign general validation
                model_roles[model] = "syntax_checker"  # Default fallback
        
        return model_roles

    def _prepare_validation_prompt(self, request, role_description: str) -> str:
        """Prepare the validation prompt for free models."""
        
        base_prompt = f"""Please provide validation feedback for the following request:

REQUEST: {request.proposal}

FOCUS AREA: {request.focus or 'general'}

YOUR VALIDATION ROLE: {role_description}

Please provide clear, constructive feedback focusing on your assigned role. 
Keep feedback practical and actionable within the scope of basic validation.
"""
        
        return base_prompt

    # Required abstract methods from BaseTool
    def get_request_model(self):
        """Return the quickreview workflow-specific request model."""
        return QuickReviewRequest

    async def prepare_prompt(self, request) -> str:
        """Not used - workflow tools use execute_workflow()."""
        return ""  # Workflow tools use execute_workflow() directly