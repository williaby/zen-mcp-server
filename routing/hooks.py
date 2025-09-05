"""
Tool Hooks for Model Routing Integration

This module provides specialized hooks for different tool types to enable
better context extraction and prompt analysis for intelligent model routing.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class ToolHook(ABC):
    """Abstract base class for tool-specific hooks."""

    @abstractmethod
    def get_tool_names(self) -> List[str]:
        """Get list of tool names this hook handles."""
        pass

    @abstractmethod
    def build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build analysis prompt from tool context."""
        pass

    def extract_complexity_indicators(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tool-specific complexity indicators."""
        return {}

    def suggest_model_preferences(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest model preferences based on tool-specific knowledge."""
        return {}

class ChatHook(ToolHook):
    """Hook for chat/general conversation tools."""

    def get_tool_names(self) -> List[str]:
        return ["chat", "ChatTool"]

    def build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build analysis prompt for chat tools."""
        prompt_parts = ["General chat/conversation task"]

        if context.get("files"):
            prompt_parts.append(f"involving {len(context['files'])} files")

        if context.get("file_types"):
            file_types = set(context.get("file_types", []))
            if file_types:
                prompt_parts.append(f"with file types: {', '.join(file_types)}")

        return "; ".join(prompt_parts)

    def extract_complexity_indicators(self, context: Dict[str, Any]) -> Dict[str, Any]:
        indicators = {}

        # Chat with code files suggests higher complexity
        file_types = set(context.get("file_types", []))
        code_extensions = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".rs", ".go"}
        if file_types.intersection(code_extensions):
            indicators["code_context"] = True

        return indicators

class CodeReviewHook(ToolHook):
    """Hook for code review tools."""

    def get_tool_names(self) -> List[str]:
        return ["codereview", "CodeReviewTool", "quickreview"]

    def build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build analysis prompt for code review tools."""
        prompt_parts = ["Code review and analysis task"]

        files_count = len(context.get("files", []))
        if files_count > 0:
            prompt_parts.append(f"reviewing {files_count} files")

        file_types = set(context.get("file_types", []))
        if file_types:
            prompt_parts.append(f"languages: {', '.join(file_types)}")

        return "; ".join(prompt_parts)

    def extract_complexity_indicators(self, context: Dict[str, Any]) -> Dict[str, Any]:
        indicators = {}

        # Multiple files indicate higher complexity
        files_count = len(context.get("files", []))
        if files_count > 5:
            indicators["large_codebase"] = True
        elif files_count > 1:
            indicators["multi_file_review"] = True

        # Complex language types
        file_types = set(context.get("file_types", []))
        complex_types = {".cpp", ".c", ".rs", ".scala", ".hs"}
        if file_types.intersection(complex_types):
            indicators["complex_languages"] = True

        return indicators

    def suggest_model_preferences(self, context: Dict[str, Any]) -> Dict[str, Any]:
        preferences = {}

        # Code review benefits from models with good reasoning
        preferences["prefer_reasoning_models"] = True

        # Large codebases need models with large context windows
        if len(context.get("files", [])) > 3:
            preferences["require_large_context"] = True

        return preferences

class DebugHook(ToolHook):
    """Hook for debugging tools."""

    def get_tool_names(self) -> List[str]:
        return ["debug", "DebugIssueTool"]

    def build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build analysis prompt for debugging tools."""
        prompt_parts = ["Code debugging and issue resolution task"]

        if context.get("error"):
            prompt_parts.append("with specific error context")

        files_count = len(context.get("files", []))
        if files_count > 0:
            prompt_parts.append(f"debugging {files_count} files")

        return "; ".join(prompt_parts)

    def extract_complexity_indicators(self, context: Dict[str, Any]) -> Dict[str, Any]:
        indicators = {}

        # Error context increases complexity
        if context.get("error"):
            indicators["has_error_context"] = True

        # Debugging is inherently complex
        indicators["debugging_task"] = True

        return indicators

    def suggest_model_preferences(self, context: Dict[str, Any]) -> Dict[str, Any]:
        preferences = {}

        # Debugging benefits from analytical models
        preferences["prefer_analytical_models"] = True
        preferences["avoid_creative_models"] = True

        return preferences

class AnalyzeHook(ToolHook):
    """Hook for analysis tools."""

    def get_tool_names(self) -> List[str]:
        return ["analyze", "AnalyzeTool"]

    def build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build analysis prompt for analysis tools."""
        prompt_parts = ["Code analysis and understanding task"]

        files_count = len(context.get("files", []))
        if files_count > 0:
            prompt_parts.append(f"analyzing {files_count} files")

        file_types = set(context.get("file_types", []))
        if file_types:
            prompt_parts.append(f"file types: {', '.join(file_types)}")

        return "; ".join(prompt_parts)

    def extract_complexity_indicators(self, context: Dict[str, Any]) -> Dict[str, Any]:
        indicators = {}

        # Large analysis tasks
        files_count = len(context.get("files", []))
        if files_count > 10:
            indicators["large_analysis"] = True
        elif files_count > 3:
            indicators["moderate_analysis"] = True

        return indicators

class ConsensusHook(ToolHook):
    """Hook for consensus tools."""

    def get_tool_names(self) -> List[str]:
        return ["consensus", "ConsensusTool", "layered_consensus"]

    def build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build analysis prompt for consensus tools."""
        prompt_parts = ["Multi-model consensus and decision-making task"]

        if context.get("files"):
            prompt_parts.append(f"involving {len(context['files'])} files")

        return "; ".join(prompt_parts)

    def extract_complexity_indicators(self, context: Dict[str, Any]) -> Dict[str, Any]:
        indicators = {}

        # Consensus tasks are inherently complex
        indicators["consensus_task"] = True
        indicators["requires_multiple_models"] = True

        return indicators

    def suggest_model_preferences(self, context: Dict[str, Any]) -> Dict[str, Any]:
        preferences = {}

        # Consensus benefits from diverse model types
        preferences["prefer_diverse_models"] = True
        preferences["require_multiple_capabilities"] = True

        return preferences

class PlannerHook(ToolHook):
    """Hook for planning tools."""

    def get_tool_names(self) -> List[str]:
        return ["planner", "PlannerTool"]

    def build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build analysis prompt for planning tools."""
        return "Project planning and task organization"

    def extract_complexity_indicators(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"planning_task": True}

class SecauditHook(ToolHook):
    """Hook for security audit tools."""

    def get_tool_names(self) -> List[str]:
        return ["secaudit", "SecauditTool"]

    def build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build analysis prompt for security audit tools."""
        prompt_parts = ["Security audit and vulnerability analysis"]

        files_count = len(context.get("files", []))
        if files_count > 0:
            prompt_parts.append(f"auditing {files_count} files")

        return "; ".join(prompt_parts)

    def extract_complexity_indicators(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"security_analysis": True, "expert_level": True}

    def suggest_model_preferences(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"require_security_knowledge": True, "prefer_senior_models": True}

class RefactorHook(ToolHook):
    """Hook for refactoring tools."""

    def get_tool_names(self) -> List[str]:
        return ["refactor", "RefactorTool"]

    def build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build analysis prompt for refactoring tools."""
        prompt_parts = ["Code refactoring and restructuring task"]

        files_count = len(context.get("files", []))
        if files_count > 0:
            prompt_parts.append(f"refactoring {files_count} files")

        return "; ".join(prompt_parts)

    def extract_complexity_indicators(self, context: Dict[str, Any]) -> Dict[str, Any]:
        indicators = {}

        # Refactoring complexity depends on scope
        files_count = len(context.get("files", []))
        if files_count > 5:
            indicators["large_refactoring"] = True
        elif files_count > 1:
            indicators["multi_file_refactoring"] = True

        return indicators

class ToolHooks:
    """Main hooks manager for routing integration."""

    def __init__(self):
        self.hooks: Dict[str, ToolHook] = {}
        self._register_default_hooks()

    def _register_default_hooks(self):
        """Register default hooks for common tools."""
        hooks = [
            ChatHook(),
            CodeReviewHook(),
            DebugHook(),
            AnalyzeHook(),
            ConsensusHook(),
            PlannerHook(),
            SecauditHook(),
            RefactorHook()
        ]

        for hook in hooks:
            for tool_name in hook.get_tool_names():
                self.hooks[tool_name.lower()] = hook

    def build_analysis_prompt(self, tool_name: str, context: Dict[str, Any]) -> Optional[str]:
        """Build analysis prompt using appropriate hook."""
        hook = self.hooks.get(tool_name.lower())
        if hook:
            return hook.build_analysis_prompt(context)

        # Generic fallback
        return f"Tool: {tool_name}"

    def extract_complexity_indicators(self, tool_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract complexity indicators using appropriate hook."""
        hook = self.hooks.get(tool_name.lower())
        if hook:
            return hook.extract_complexity_indicators(context)
        return {}

    def suggest_model_preferences(self, tool_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get model preferences using appropriate hook."""
        hook = self.hooks.get(tool_name.lower())
        if hook:
            return hook.suggest_model_preferences(context)
        return {}

    def register_hook(self, tool_name: str, hook: ToolHook):
        """Register a custom hook for a tool."""
        self.hooks[tool_name.lower()] = hook

    def get_available_hooks(self) -> List[str]:
        """Get list of available hook names."""
        return list(self.hooks.keys())
