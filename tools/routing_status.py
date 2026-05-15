"""
Routing Status Tool -- inspect the dynamic model routing subsystem.

Read-only introspection for the fork's dynamic routing system (see
``routing/integration.py``). Reports whether routing is enabled, lists
available models by org-level band, shows usage statistics, dumps the
active routing configuration, and can return a structured model
recommendation for an ad-hoc prompt.

Routing is gated by the ``ZEN_SMART_ROUTING`` environment variable
(``true`` to enable). When disabled, the tool returns a help message
explaining how to turn routing on. When the routing module itself is
not importable (missing dependencies, partial install), the tool returns
a "NOT AVAILABLE" message instead of raising.

This tool does NOT call any AI model; it only reports on the routing
state and asks the routing integration for recommendations. It is safe
to invoke at any time, including before any routing decisions have been
made (stats will simply be zero).
"""

from typing import Any, Optional

from pydantic import Field

from tools.shared.base_models import ToolRequest
from tools.simple.base import SimpleTool


class RoutingStatusRequest(ToolRequest):
    """Request model for routing status queries."""

    action: str = Field(
        default="status",
        description=(
            "Which view to return. One of: "
            "'status' (default; enabled/model counts/totals), "
            "'models' (models grouped by org level: free/junior/senior/executive), "
            "'stats' (decision counts, success rate, free-model selections, savings), "
            "'config' (active routing thresholds and settings), "
            "'recommend' (return a model recommendation for the given prompt -- "
            "requires the 'prompt' field). Any other value returns an error string."
        ),
    )
    prompt: Optional[str] = Field(
        default=None,
        description=(
            "Prompt text to get a routing recommendation for. REQUIRED when "
            "action='recommend'; ignored otherwise. Should be the actual user-facing "
            "prompt so the complexity analyzer can score it."
        ),
    )
    context: Optional[dict[str, Any]] = Field(
        default=None,
        description=(
            "Optional context object that improves recommendations. Only used when "
            "action='recommend'. Recognized keys: 'files' (list[str] of absolute "
            "paths), 'file_types' (list[str] of extensions like '.py'), 'tool_name' "
            "(str: which tool will run the prompt), 'error' (str: error text if "
            "this is a debugging request). Unknown keys are ignored."
        ),
    )


class RoutingStatusTool(SimpleTool):
    """
    Inspect the dynamic model routing subsystem (read-only).

    Returns markdown-formatted reports describing the state of the
    fork's routing integration. Supports five views via the ``action``
    parameter -- status, models, stats, config, recommend.

    Backend / availability:
    - Driven by ``routing.integration.get_integration_instance()``.
    - If ``ZEN_SMART_ROUTING`` is not ``true``, returns a help message
      explaining how to enable routing -- does NOT raise.
    - If the ``routing`` module fails to import, returns a "NOT
      AVAILABLE" message -- does NOT raise.

    This tool never calls an external LLM. ``requires_model()`` returns
    False, so the MCP client will not pass a ``model`` argument.

    Return value:
    - String containing a markdown report. The synchronous body is wrapped
      into the standard MCP text-content response by ``SimpleTool``.

    Limitations:
    - Stats reset on each server restart (in-memory).
    - The 'recommend' action requires ``prompt``; missing it returns an
      error string rather than raising.
    """

    def get_name(self) -> str:
        return "routing_status"

    def get_description(self) -> str:
        return (
            "Inspects the dynamic model routing subsystem and returns a markdown report. "
            "Pick a view via action: status (enabled/totals), models (by org level), "
            "stats (decisions/success rate/savings), config (thresholds), or "
            "recommend (model pick for a given prompt -- requires prompt). "
            "Read-only; never calls an LLM. Returns help text if routing is disabled "
            "(ZEN_SMART_ROUTING=true required) or the routing module is missing."
        )

    def get_tool_fields(self) -> dict[str, Any]:
        """Return tool-specific field definitions for schema generation."""
        return {
            "action": {
                "type": "string",
                "default": "status",
                "enum": ["status", "models", "stats", "config", "recommend"],
                "description": (
                    "Which view to return. "
                    "status=enabled flag, model totals, success rate summary. "
                    "models=available models grouped by org level (free/junior/senior/executive). "
                    "stats=decision counts, success rate, free-model rate, est. savings. "
                    "config=active routing thresholds and per-level cost limits. "
                    "recommend=structured model recommendation for the given prompt (requires 'prompt')."
                ),
            },
            "prompt": {
                "type": "string",
                "description": (
                    "Prompt text to get a recommendation for. REQUIRED when action='recommend'; "
                    "ignored otherwise. Pass the actual user-facing prompt so the complexity "
                    "analyzer can score it accurately."
                ),
            },
            "context": {
                "type": "object",
                "description": (
                    "Optional context to improve recommendations. Used only when action='recommend'. "
                    "Unknown keys are ignored."
                ),
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Absolute paths of files in scope. Used to weight long-context models.",
                    },
                    "file_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File extensions like '.py' or '.ts'. Biases toward code-specialized models.",
                    },
                    "tool_name": {
                        "type": "string",
                        "description": "Name of the calling tool (e.g. 'chat', 'codereview'). Used for per-tool routing policy.",
                    },
                    "error": {
                        "type": "string",
                        "description": "Error message if this is a debugging request. Biases toward reasoning-strong models.",
                    },
                },
            },
        }

    def get_required_fields(self) -> list[str]:
        """Return list of required field names."""
        return []  # No required fields, action defaults to "status"

    def get_system_prompt(self) -> str:
        return """You are a routing status assistant. Your role is to provide information about the dynamic model routing system:

1. **Status Information**: Show whether routing is enabled, model counts, and system health
2. **Model Information**: List available models by level (free, junior, senior, executive)
3. **Usage Statistics**: Show routing decisions, success rates, and cost savings
4. **Configuration Details**: Display routing rules and thresholds
5. **Model Recommendations**: Suggest optimal models for specific prompts and contexts

Always format information clearly and highlight key insights about routing behavior."""

    async def execute_tool(self, request: RoutingStatusRequest) -> str:
        """Execute the routing status tool."""

        try:
            # Try to import routing components
            from routing.integration import get_integration_instance

            integration = get_integration_instance()

            if not integration.enabled:
                return self._format_disabled_response()

            # Handle different actions
            if request.action == "status":
                return self._get_general_status(integration)
            elif request.action == "models":
                return self._get_models_info(integration)
            elif request.action == "stats":
                return self._get_statistics(integration)
            elif request.action == "config":
                return self._get_configuration(integration)
            elif request.action == "recommend":
                if not request.prompt:
                    return "Error: 'prompt' is required for recommendation action"
                return self._get_recommendation(integration, request.prompt, request.context or {})
            else:
                return (
                    f"Error: Unknown action '{request.action}'. Valid actions: status, models, stats, config, recommend"
                )

        except ImportError:
            return self._format_not_available_response()
        except Exception as e:
            return f"Error accessing routing system: {str(e)}"

    def _format_disabled_response(self) -> str:
        """Format response when routing is disabled."""
        return """# Dynamic Model Routing Status

**Status**: ❌ DISABLED

Dynamic model routing is not enabled. To enable:

1. Set environment variable: `ZEN_SMART_ROUTING=true`
2. Restart the server
3. Routing will automatically begin optimizing model selection

**Benefits of enabling routing**:
- Automatic free model prioritization
- Cost optimization (20-30% typical savings)
- Task complexity-based model selection
- Intelligent fallback handling
- Performance tracking and learning

Use `ZEN_SMART_ROUTING=true ./run-server.sh` to enable routing."""

    def _format_not_available_response(self) -> str:
        """Format response when routing system is not available."""
        return """# Dynamic Model Routing Status

**Status**: ❌ NOT AVAILABLE

The dynamic model routing system is not installed or not available.

This may happen if:
- The routing module is not installed
- Required dependencies are missing
- Server was started without routing support

Please check your installation or contact support for assistance."""

    def _get_general_status(self, integration) -> str:
        """Get general routing status."""
        stats = integration.get_routing_stats()

        status_icon = "✅" if integration.enabled else "❌"

        response = f"""# Dynamic Model Routing Status

**Status**: {status_icon} ENABLED

## System Information
- **Total Models**: {stats.get("total_models", 0)}
- **Available Models**: {stats.get("available_models", 0)}
- **Cache Size**: {stats.get("cache_size", 0)} entries

## Routing Activity
- **Total Decisions**: {stats.get("routing_decisions", 0)}
- **Successful Routes**: {stats.get("routing_successes", 0)}
- **Route Failures**: {stats.get("routing_failures", 0)}
- **Success Rate**: {stats.get("success_rate", 0):.1%}

## Cost Optimization
- **Free Model Selections**: {stats.get("free_model_selections", 0)}
- **Estimated Savings**: ${stats.get("cost_savings", 0):.4f}

**Routing is actively optimizing model selection for cost and performance.**"""

        return response

    def _get_models_info(self, integration) -> str:
        """Get information about available models."""
        if not integration.router:
            return "Router not available"

        stats = integration.router.get_model_stats()
        models_by_level = stats.get("models_by_level", {})

        response = ["# Available Models by Level\n"]

        level_icons = {"free": "🆓", "junior": "🥉", "senior": "🥈", "executive": "🥇"}

        for level, info in models_by_level.items():
            icon = level_icons.get(level, "⭐")
            total = info.get("total", 0)
            available = info.get("available", 0)
            avg_success = info.get("average_success_rate", 0)

            response.append(f"## {icon} {level.title()} Level")
            response.append(f"- **Total Models**: {total}")
            response.append(f"- **Available**: {available}")
            response.append(f"- **Average Success Rate**: {avg_success:.1%}")

            # Get specific models for this level
            try:
                level_models = integration.router.get_models_by_level(level)
                if level_models:
                    response.append("- **Models**:")
                    for model in level_models[:5]:  # Show first 5
                        name = model["name"]
                        cost = model["cost_per_token"]
                        if cost == 0:
                            cost_str = "Free"
                        else:
                            cost_str = f"${cost:.4f}/token"
                        response.append(f"  - {name} ({cost_str})")
                    if len(level_models) > 5:
                        response.append(f"  - ... and {len(level_models) - 5} more")
            except Exception:
                pass  # Skip model details if not available

            response.append("")

        # Top performers
        top_performers = stats.get("top_performers", [])
        if top_performers:
            response.append("## 🏆 Top Performing Models")
            for i, model in enumerate(top_performers[:3], 1):
                name = model["name"]
                level = model["level"]
                success_rate = model["success_rate"]
                requests = model["total_requests"]
                response.append(f"{i}. **{name}** ({level}) - {success_rate:.1%} success rate ({requests} requests)")

        return "\n".join(response)

    def _get_statistics(self, integration) -> str:
        """Get detailed routing statistics."""
        stats = integration.get_routing_stats()

        total_decisions = stats.get("routing_decisions", 0)
        successes = stats.get("routing_successes", 0)
        failures = stats.get("routing_failures", 0)
        free_selections = stats.get("free_model_selections", 0)

        response = f"""# Routing Statistics

## Decision Summary
- **Total Routing Decisions**: {total_decisions:,}
- **Successful Routes**: {successes:,}
- **Failed Routes**: {failures:,}
- **Success Rate**: {(successes / total_decisions * 100) if total_decisions > 0 else 0:.1f}%

## Cost Optimization
- **Free Model Selections**: {free_selections:,}
- **Free Model Rate**: {(free_selections / total_decisions * 100) if total_decisions > 0 else 0:.1f}%
- **Estimated Cost Savings**: ${stats.get("cost_savings", 0):.4f}

## Performance Metrics
- **Cache Hit Rate**: Efficient routing decisions cached
- **Average Decision Time**: < 50ms target
- **Model Availability**: {stats.get("available_models", 0)}/{stats.get("total_models", 0)} models online

## Routing Effectiveness
{"✅" if (total_decisions > 0 and (successes / total_decisions) > 0.9) else "⚠️"} **Overall Performance**: {"Excellent" if (total_decisions > 0 and (successes / total_decisions) > 0.9) else "Needs attention"}
{"✅" if (total_decisions > 0 and (free_selections / total_decisions) > 0.5) else "⚠️"} **Cost Efficiency**: {"Good" if (total_decisions > 0 and (free_selections / total_decisions) > 0.5) else "Could improve"}

*Statistics reset with each server restart*"""

        return response

    def _get_configuration(self, integration) -> str:
        """Get routing configuration information."""
        if not integration.router:
            return "Router configuration not available"

        config = integration.router.routing_config

        response = ["# Routing Configuration\n"]

        # Routing levels
        response.append("## Model Levels")
        levels = config.get("levels", {})
        for level, settings in levels.items():
            cost_limit = settings.get("cost_limit", "N/A")
            priority = settings.get("priority", "N/A")
            response.append(f"- **{level.title()}**: Cost limit ${cost_limit}, Priority {priority}")

        response.append("")

        # Complexity thresholds
        response.append("## Complexity Thresholds")
        thresholds = config.get("complexity_thresholds", {})
        for complexity, settings in thresholds.items():
            max_level = settings.get("max_level", "N/A")
            confidence = settings.get("confidence_threshold", "N/A")
            response.append(f"- **{complexity.title()}**: Max level {max_level}, Confidence threshold {confidence}")

        response.append("")

        # Settings
        response.append("## Routing Settings")
        response.append(f"- **Free Model Preference**: {'✅' if config.get('free_model_preference') else '❌'}")
        response.append(f"- **Cost Optimization**: {'✅' if config.get('cost_optimization') else '❌'}")
        response.append(f"- **Fallback Strategy**: {config.get('fallback_strategy', 'escalate')}")

        return "\n".join(response)

    def _get_recommendation(self, integration, prompt: str, context: dict[str, Any]) -> str:
        """Get model recommendation for a specific prompt."""
        recommendation = integration.get_model_recommendation(prompt, context)

        if "error" in recommendation:
            return f"Error getting recommendation: {recommendation['error']}"

        model_name = recommendation.get("model", "Unknown")
        level = recommendation.get("level", "Unknown")
        confidence = recommendation.get("confidence", 0)
        reasoning = recommendation.get("reasoning", "No reasoning provided")
        cost = recommendation.get("estimated_cost", 0)
        fallbacks = recommendation.get("fallback_models", [])

        response = f"""# Model Recommendation

**Prompt**: "{prompt[:100]}{"..." if len(prompt) > 100 else ""}"

## Recommended Model
- **Model**: {model_name}
- **Level**: {level}
- **Confidence**: {confidence:.1%}
- **Estimated Cost**: ${cost:.6f}

## Reasoning
{reasoning}

## Alternative Models
"""

        if fallbacks:
            for i, fallback in enumerate(fallbacks[:3], 1):
                response += f"{i}. {fallback}\n"
        else:
            response += "No alternatives available\n"

        # Context analysis
        if context:
            response += "\n## Context Analysis\n"
            if context.get("files"):
                response += f"- **Files**: {len(context['files'])} files\n"
            if context.get("file_types"):
                response += f"- **File Types**: {', '.join(set(context['file_types']))}\n"
            if context.get("tool_name"):
                response += f"- **Tool**: {context['tool_name']}\n"
            if context.get("error"):
                response += "- **Error Context**: Present\n"

        return response

    def requires_model(self) -> bool:
        """This tool doesn't require AI model access."""
        return False

    async def prepare_prompt(self, request: RoutingStatusRequest) -> str:
        """Prepare prompt for the tool execution."""
        # This tool doesn't use AI models, so return empty prompt
        return ""
