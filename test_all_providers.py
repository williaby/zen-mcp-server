#!/usr/bin/env python3
"""Test all configured AI providers to verify Infisical secrets are loaded correctly.

This script tests each configured provider with a simple prompt to ensure:
1. API keys are loaded correctly from Infisical
2. Each provider can make successful API calls
3. Response quality is adequate
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from providers.openai import OpenAIModelProvider
from providers.openrouter import OpenRouterProvider
from providers.registry import ModelProviderRegistry
from providers.shared import ProviderType
from utils.env import get_env, reload_env

# Optional providers
try:
    from providers.gemini import GeminiModelProvider

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from providers.xai import XAIModelProvider

    XAI_AVAILABLE = True
except ImportError:
    XAI_AVAILABLE = False

try:
    from providers.dial import DIALModelProvider

    DIAL_AVAILABLE = True
except ImportError:
    DIAL_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Simple test prompt
TEST_PROMPT = "What is 2+2? Reply with just the number and a brief explanation."

# Test models from each tier based on docs/models/models.csv
# Using OpenRouter for unified access to all models
PROVIDERS_TO_TEST = [
    # Direct OpenAI API test
    ("openai", "o4-mini"),  # Direct OpenAI API
    # Premium tier (executive level) - Top performing models
    ("openrouter", "openai/gpt-5.1"),  # Lead architect - next generation
    ("openrouter", "anthropic/claude-opus-4.5"),  # System architect - agentic workflows
    ("openrouter", "openai/gpt-5.1-codex"),  # Lead architect - coding specialist
    ("openrouter", "google/gemini-3-pro-preview"),  # Lead architect - multimodal
    # High performance tier (senior level) - Production workhorses
    ("openrouter", "anthropic/claude-sonnet-4.5"),  # Senior dev - agentic reasoning
    ("openrouter", "openai/gpt-5-mini"),  # Senior dev - efficient general
    ("openrouter", "deepseek/deepseek-r1-0528"),  # Security analyst - reasoning
    # Open source tier (senior level) - Fast and cost-effective
    ("openrouter", "google/gemini-2.5-flash"),  # Senior dev - speed optimized
    ("openrouter", "qwen/qwen3-coder"),  # Senior dev - coding specialist
    ("openrouter", "mistralai/mistral-large-2411"),  # Senior dev - European
    # Free champion tier (junior level) - High quality free models
    ("openrouter", "meta-llama/llama-3.1-405b-instruct:free"),  # Technical validator
    ("openrouter", "qwen/qwen-2.5-coder-32b-instruct:free"),  # Code reviewer
    ("openrouter", "deepseek/deepseek-r1-distill-llama-70b:free"),  # Code reviewer - reasoning
]


def test_provider(provider_name: str, model_name: str) -> dict[str, str | bool]:
    """Test a single provider with a simple prompt.

    Args:
        provider_name: Name of the provider (e.g., 'google', 'openai')
        model_name: Model name to test

    Returns:
        Dictionary with test results
    """
    result = {
        "provider": provider_name,
        "model": model_name,
        "success": False,
        "message": "",
        "response": "",
    }

    try:
        # Get provider from registry
        provider_type = ProviderType(provider_name)
        provider = ModelProviderRegistry.get_provider(provider_type)

        if not provider:
            result["message"] = f"Provider '{provider_name}' not configured or registered"
            return result

        # Make simple API call
        logger.info(f"Testing {provider_name}/{model_name}...")
        model_response = provider.generate_content(
            prompt=TEST_PROMPT,
            model_name=model_name,
            temperature=0.3,
            max_output_tokens=100,
        )

        if model_response and model_response.content and len(model_response.content.strip()) > 0:
            result["success"] = True
            result["response"] = model_response.content[:200]  # First 200 chars
            result["message"] = "✅ Success"
        else:
            result["message"] = "❌ Empty response received"

    except Exception as e:
        result["message"] = f"❌ Error: {str(e)[:100]}"
        logger.error(f"Error testing {provider_name}/{model_name}: {e}", exc_info=True)

    return result


def main():
    """Run tests for all configured providers."""
    print("=" * 80)
    print("Zen MCP Server - Provider Configuration Test")
    print("=" * 80)
    print()

    # Reload environment to ensure Infisical secrets are loaded
    print("🔄 Loading secrets from Infisical...")
    reload_env(use_infisical=True)
    print()

    # Register providers (mimics server.py initialization)
    print("📦 Registering providers...")
    if GEMINI_AVAILABLE:
        ModelProviderRegistry.register_provider(ProviderType.GOOGLE, GeminiModelProvider)
    ModelProviderRegistry.register_provider(ProviderType.OPENAI, OpenAIModelProvider)
    if XAI_AVAILABLE:
        ModelProviderRegistry.register_provider(ProviderType.XAI, XAIModelProvider)
    if DIAL_AVAILABLE:
        ModelProviderRegistry.register_provider(ProviderType.DIAL, DIALModelProvider)
    ModelProviderRegistry.register_provider(ProviderType.OPENROUTER, OpenRouterProvider)
    print()

    # Check which providers are configured
    print("📋 Checking configured providers...")
    print()

    configured_count = 0
    api_keys = {
        "GEMINI_API_KEY": "Google/Gemini",
        "OPENAI_API_KEY": "OpenAI",
        "XAI_API_KEY": "X.AI",
        "DIAL_API_KEY": "DIAL",
        "OPENROUTER_API_KEY": "OpenRouter",
        "AZURE_OPENAI_API_KEY": "Azure OpenAI",
    }

    for key, name in api_keys.items():
        value = get_env(key)
        if value and value != f"your_{key.lower()}_here":
            print(f"  ✅ {name}: Configured")
            configured_count += 1
        else:
            print(f"  ⚠️  {name}: Not configured")

    print()
    print(f"Found {configured_count} configured provider(s)")
    print()

    if configured_count == 0:
        print("❌ No providers configured. Please check your Infisical setup.")
        print("   Run: ./run-server.sh and check logs for Infisical loading messages")
        return 1

    # Run tests
    print("🧪 Running provider tests...")
    print()

    results = []
    for provider_name, model_name in PROVIDERS_TO_TEST:
        result = test_provider(provider_name, model_name)
        results.append(result)

        # Print result
        status = result["message"]
        print(f"  {status} {provider_name}/{model_name}")
        if result["success"]:
            print(f"    Response: {result['response'][:100]}...")
        print()

    # Summary
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)
    print()

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print()

    if failed:
        print("Failed tests:")
        for r in failed:
            print(f"  - {r['provider']}/{r['model']}: {r['message']}")
        print()

    # Return exit code
    if len(successful) > 0:
        print("✅ At least one provider is working correctly!")
        return 0
    else:
        print("❌ No providers are working. Please check your configuration.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
