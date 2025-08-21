"""
Test data fixtures for dynamic model routing tests.

This module provides comprehensive test data including sample prompts,
model configurations, and expected routing behaviors.
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class RoutingTestCase:
    """Test case for routing behavior."""
    prompt: str
    context: Dict[str, Any]
    expected_complexity: str
    expected_task_type: str
    expected_level: str
    description: str
    prefer_free: bool = True

# Sample prompts with expected routing behavior
COMPLEXITY_TEST_CASES = [
    RoutingTestCase(
        prompt="Help me fix this simple typo in my code",
        context={"files": ["main.py"], "file_types": [".py"]},
        expected_complexity="simple",
        expected_task_type="debugging",
        expected_level="free",
        description="Simple debugging task should use free models"
    ),
    RoutingTestCase(
        prompt="Please review this Python function and suggest improvements",
        context={"files": ["utils.py"], "file_types": [".py"]},
        expected_complexity="moderate",
        expected_task_type="code_review",
        expected_level="junior",
        description="Code review should use junior level models"
    ),
    RoutingTestCase(
        prompt="Analyze this complex distributed system architecture for security vulnerabilities",
        context={"files": ["service.py", "auth.py", "database.py"], "file_types": [".py"]},
        expected_complexity="expert",
        expected_task_type="analysis",
        expected_level="executive",
        description="Complex security analysis needs executive models"
    ),
    RoutingTestCase(
        prompt="Write a comprehensive documentation for this API",
        context={"files": ["api.py"], "file_types": [".py"]},
        expected_complexity="moderate",
        expected_task_type="documentation",
        expected_level="free",
        description="Documentation tasks should prefer free models"
    ),
    RoutingTestCase(
        prompt="Implement a high-performance concurrent data structure with lock-free algorithms",
        context={"files": ["concurrent.cpp"], "file_types": [".cpp"]},
        expected_complexity="expert",
        expected_task_type="code_generation",
        expected_level="executive",
        description="Advanced concurrent programming requires executive models"
    ),
    RoutingTestCase(
        prompt="Debug this memory leak in a multi-threaded C++ application",
        context={
            "files": ["main.cpp", "worker.cpp", "memory.cpp"], 
            "file_types": [".cpp"],
            "error": "Segmentation fault in worker thread"
        },
        expected_complexity="expert",
        expected_task_type="debugging",
        expected_level="senior",
        description="Complex debugging with error context"
    ),
    RoutingTestCase(
        prompt="Create a simple hello world program",
        context={"files": [], "file_types": []},
        expected_complexity="simple",
        expected_task_type="code_generation",
        expected_level="free",
        description="Simple code generation should use free models"
    ),
    RoutingTestCase(
        prompt="Design a microservices architecture for an e-commerce platform",
        context={"files": [], "file_types": []},
        expected_complexity="expert",
        expected_task_type="planning",
        expected_level="executive",
        description="Architecture planning requires executive models"
    ),
]

# Mock model configurations for testing
MOCK_MODEL_CONFIG = {
    "models": [
        {
            "model_name": "llama3.2:free",
            "aliases": ["free-llama", "local-free"],
            "context_window": 32000,
            "max_output_tokens": 8000,
            "supports_images": False,
            "is_custom": True,
            "description": "Free local Llama model"
        },
        {
            "model_name": "qwen/qwen-2.5-coder-32b-instruct:free",
            "aliases": ["qwen-coder-free", "free-coder"],
            "context_window": 131072,
            "max_output_tokens": 32768,
            "supports_images": False,
            "description": "Free coding specialist model"
        },
        {
            "model_name": "anthropic/claude-3-haiku",
            "aliases": ["haiku", "claude-haiku"],
            "context_window": 200000,
            "max_output_tokens": 64000,
            "supports_images": True,
            "description": "Claude 3 Haiku - fast and efficient"
        },
        {
            "model_name": "anthropic/claude-3-sonnet",
            "aliases": ["sonnet", "claude-sonnet"],
            "context_window": 200000,
            "max_output_tokens": 64000,
            "supports_images": True,
            "description": "Claude 3 Sonnet - balanced performance"
        },
        {
            "model_name": "anthropic/claude-3-opus",
            "aliases": ["opus", "claude-opus"],
            "context_window": 200000,
            "max_output_tokens": 64000,
            "supports_images": True,
            "description": "Claude 3 Opus - most capable"
        },
        {
            "model_name": "openai/gpt-4",
            "aliases": ["gpt4", "gpt-4"],
            "context_window": 128000,
            "max_output_tokens": 8192,
            "supports_images": True,
            "description": "GPT-4 - advanced reasoning"
        }
    ]
}

# Expected model level mappings
EXPECTED_MODEL_LEVELS = {
    "llama3.2:free": "free",
    "qwen/qwen-2.5-coder-32b-instruct:free": "free",
    "anthropic/claude-3-haiku": "junior",
    "anthropic/claude-3-sonnet": "senior", 
    "anthropic/claude-3-opus": "executive",
    "openai/gpt-4": "executive"
}

# Test scenarios for different tool types
TOOL_SCENARIOS = {
    "chat": [
        {
            "prompt": "Explain how Python generators work",
            "context": {"tool_name": "chat"},
            "expected_level": "free",
            "reasoning": "Simple explanation task"
        },
        {
            "prompt": "Help me understand this complex React component with hooks",
            "context": {"tool_name": "chat", "files": ["component.jsx"]},
            "expected_level": "junior",
            "reasoning": "Code explanation with context"
        }
    ],
    "codereview": [
        {
            "prompt": "Review this Python function",
            "context": {"tool_name": "codereview", "files": ["function.py"]},
            "expected_level": "junior",
            "reasoning": "Standard code review"
        },
        {
            "prompt": "Security review of authentication system",
            "context": {"tool_name": "codereview", "files": ["auth.py", "security.py", "models.py"]},
            "expected_level": "senior",
            "reasoning": "Security review requires advanced analysis"
        }
    ],
    "debug": [
        {
            "prompt": "Fix this simple syntax error",
            "context": {"tool_name": "debug", "error": "SyntaxError: invalid syntax"},
            "expected_level": "free",
            "reasoning": "Simple syntax errors can be fixed by free models"
        },
        {
            "prompt": "Debug this race condition in concurrent code",
            "context": {"tool_name": "debug", "files": ["concurrent.py"], "error": "Race condition detected"},
            "expected_level": "senior",
            "reasoning": "Concurrency bugs need advanced debugging"
        }
    ],
    "analyze": [
        {
            "prompt": "Analyze code structure",
            "context": {"tool_name": "analyze", "files": ["main.py"]},
            "expected_level": "junior",
            "reasoning": "Basic code analysis"
        },
        {
            "prompt": "Analyze performance bottlenecks in distributed system",
            "context": {"tool_name": "analyze", "files": ["service1.py", "service2.py", "database.py"]},
            "expected_level": "senior",
            "reasoning": "Performance analysis of distributed systems"
        }
    ],
    "consensus": [
        {
            "prompt": "Get consensus on code style",
            "context": {"tool_name": "consensus"},
            "expected_level": "junior",
            "reasoning": "Simple consensus tasks"
        },
        {
            "prompt": "Architectural decision for microservices",
            "context": {"tool_name": "consensus", "files": ["architecture.md"]},
            "expected_level": "executive",
            "reasoning": "Complex architectural decisions need executive models"
        }
    ]
}

# Performance test data
PERFORMANCE_TEST_PROMPTS = [
    "Quick code review",
    "Explain this simple function", 
    "Debug this error message",
    "Write a basic Python script",
    "Analyze this small file"
] * 20  # 100 total prompts for performance testing

# Error handling test cases
ERROR_TEST_CASES = [
    {
        "description": "Invalid model configuration",
        "config": {"models": []},  # Empty models
        "should_fail": False,  # Should gracefully fallback
        "expected_behavior": "Use default configuration"
    },
    {
        "description": "Corrupted routing config",
        "routing_config": {"invalid": "json"},
        "should_fail": False,
        "expected_behavior": "Use default routing rules"
    },
    {
        "description": "No available models",
        "models_available": [],
        "should_fail": True,
        "expected_behavior": "Raise RuntimeError"
    }
]

# Cost optimization test cases
COST_TEST_CASES = [
    {
        "prompt": "Simple task",
        "prefer_free": True,
        "max_cost": None,
        "expected_cost": 0.0,
        "expected_model_type": "free"
    },
    {
        "prompt": "Complex analysis task",
        "prefer_free": True,
        "max_cost": 0.005,
        "expected_cost": 0.0,  # Should still prefer free
        "expected_model_type": "free"
    },
    {
        "prompt": "Expert level task",
        "prefer_free": False,
        "max_cost": 0.01,
        "expected_cost": lambda x: x > 0,  # Should use paid model
        "expected_model_type": "paid"
    }
]

# File type complexity test cases
FILE_TYPE_COMPLEXITY = {
    ".py": 0.2,      # Python - moderate
    ".js": 0.1,      # JavaScript - easy
    ".cpp": 0.5,     # C++ - complex
    ".rs": 0.4,      # Rust - complex
    ".md": 0.0,      # Markdown - simple
    ".json": 0.0,    # JSON - simple
    ".yaml": 0.1,    # YAML - slightly complex
    ".sql": 0.3,     # SQL - moderate to complex
}

def get_test_case_by_id(test_id: str) -> RoutingTestCase:
    """Get a specific test case by ID."""
    test_cases = {case.description.lower().replace(" ", "_"): case for case in COMPLEXITY_TEST_CASES}
    return test_cases.get(test_id)

def get_tool_scenarios(tool_name: str) -> List[Dict[str, Any]]:
    """Get test scenarios for a specific tool."""
    return TOOL_SCENARIOS.get(tool_name, [])

def create_mock_context(tool_name: str = "test", 
                       files: List[str] = None, 
                       error: str = None) -> Dict[str, Any]:
    """Create a mock context for testing."""
    context = {"tool_name": tool_name}
    
    if files:
        context["files"] = files
        context["file_types"] = [f.split(".")[-1] for f in files if "." in f]
    
    if error:
        context["error"] = error
    
    return context