"""
Tool category mappings for the Zen MCP Hub

Maps task categories to specific MCP tools across all connected servers.
This configuration drives the dynamic tool filtering based on query context.
"""

from typing import Dict, List, Set

# Core tools that are always available (minimal context)
CORE_TOOLS: Set[str] = {
    # Essential Zen tools
    "mcp__zen__chat",
    "mcp__zen__listmodels", 
    "mcp__zen__challenge",
    
    # Essential Claude Code tools
    "Read", "Write", "Edit", "Bash",
    
    # Essential git
    "mcp__git__git_status"
}

# Tool category mappings - maps detection categories to tool lists
TOOL_CATEGORY_MAPPINGS: Dict[str, Dict[str, List[str]]] = {
    # Development and debugging tools
    "development": {
        "zen": [
            "mcp__zen__debug",
            "mcp__zen__codereview", 
            "mcp__zen__analyze",
            "mcp__zen__refactor",
            "mcp__zen__testgen"
        ],
        "claude_code": [
            "Read", "Write", "Edit", "MultiEdit", 
            "Glob", "Grep", "Bash"
        ],
        "git": [
            "mcp__git__git_status", "mcp__git__git_diff",
            "mcp__git__git_commit", "mcp__git__git_add"
        ]
    },
    
    # Complex analysis and planning
    "workflow": {
        "zen": [
            "mcp__zen__consensus",
            "mcp__zen__thinkdeep",
            "mcp__zen__planner", 
            "mcp__zen__precommit"
        ],
        "reasoning": [
            "mcp__sequential-thinking__sequentialthinking"
        ],
        "git": [
            "mcp__git__git_log", "mcp__git__git_branch",
            "mcp__git__git_checkout", "mcp__git__git_create_branch"
        ]
    },
    
    # Security and specialized analysis
    "specialized": {
        "zen": [
            "mcp__zen__secaudit",
            "mcp__zen__docgen",
            "mcp__zen__tracer"
        ],
        "security": [
            "mcp__safety-mcp-sse__check_package_security",
            "mcp__safety-mcp-sse__get_recommended_version",
            "mcp__safety-mcp-sse__list_vulnerabilities_affecting_version"
        ],
        "documentation": [
            "mcp__context7-sse__resolve-library-id",
            "mcp__context7-sse__get-library-docs"
        ]
    },
    
    # Time and utility tools
    "utilities": {
        "time": [
            "mcp__time__get_current_time",
            "mcp__time__convert_time"
        ],
        "claude_code": [
            "WebFetch", "WebSearch", "TodoWrite"
        ]
    }
}

# Tool priorities for when multiple categories match
TOOL_PRIORITIES: Dict[str, int] = {
    # Higher priority = more likely to be included
    "mcp__zen__debug": 100,
    "mcp__zen__codereview": 95,
    "mcp__zen__consensus": 90,
    "mcp__zen__chat": 85,
    "Read": 80,
    "Write": 80,
    "Edit": 80,
    "Bash": 75,
    "mcp__git__git_status": 70,
    "mcp__git__git_commit": 65,
}

def get_tools_for_categories(categories: Set[str]) -> List[str]:
    """
    Get the list of tools for given categories.
    
    Args:
        categories: Set of category names (e.g., {'development', 'git'})
        
    Returns:
        List of tool names to include
    """
    tools = set(CORE_TOOLS)  # Always include core tools
    
    for category in categories:
        if category in TOOL_CATEGORY_MAPPINGS:
            category_tools = TOOL_CATEGORY_MAPPINGS[category]
            for server_tools in category_tools.values():
                tools.update(server_tools)
    
    # Sort by priority if available, otherwise alphabetically
    return sorted(tools, key=lambda t: (-TOOL_PRIORITIES.get(t, 0), t))

def get_server_for_tool(tool_name: str) -> str:
    """
    Determine which MCP server handles a specific tool.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Server identifier
    """
    if tool_name.startswith("mcp__zen__"):
        return "zen"
    elif tool_name.startswith("mcp__git__"):
        return "git"
    elif tool_name.startswith("mcp__time__"):
        return "time"
    elif tool_name.startswith("mcp__sequential-thinking__"):
        return "sequential-thinking"
    elif tool_name.startswith("mcp__context7-sse__"):
        return "context7-sse"
    elif tool_name.startswith("mcp__safety-mcp-sse__"):
        return "safety-mcp-sse"
    else:
        return "claude_code"  # Built-in Claude Code tools