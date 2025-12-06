"""Infisical integration for Zen MCP Server.

This module provides integration with Infisical for centralized secrets management.
It supports both Infisical CLI and Python SDK approaches with graceful fallback
to traditional .env file loading.

Architecture:
    1. Try Infisical SDK (if available and configured)
    2. Fall back to Infisical CLI (if installed)
    3. Fall back to .env file (traditional approach)

Usage:
    from utils.infisical import load_secrets_from_infisical

    # Load secrets (auto-detects best method)
    secrets = load_secrets_from_infisical()

    # Inject into environment
    for key, value in secrets.items():
        os.environ[key] = value
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Try to import Infisical SDK (optional dependency)
try:
    from infisical_client import ClientSettings, InfisicalClient
    from infisical_client.schemas import ListSecretsOptions

    INFISICAL_SDK_AVAILABLE = True
except ImportError:
    INFISICAL_SDK_AVAILABLE = False
    logger.debug("Infisical Python SDK not available (install with: pip install infisical-python)")


def _get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).resolve().parent.parent


def _load_infisical_config() -> dict[str, Any] | None:
    """Load Infisical configuration from .infisical.json."""
    config_path = _get_project_root() / ".infisical.json"
    if not config_path.exists():
        logger.debug("No .infisical.json found")
        return None

    try:
        with open(config_path) as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load .infisical.json: {e}")
        return None


def _get_infisical_token() -> str | None:
    """Get Infisical access token from environment.

    The Infisical SDK v2+ uses a single access_token for authentication.
    This can be a Machine Identity token or a Universal Auth token.
    """
    # Check for access token (machine identity or universal auth)
    token = os.getenv("INFISICAL_TOKEN")
    if token:
        return token

    # Also check INFISICAL_ACCESS_TOKEN as an alternative
    token = os.getenv("INFISICAL_ACCESS_TOKEN")
    if token:
        return token

    return None


def _get_cloudflare_access_headers() -> dict[str, str]:
    """Get Cloudflare Access headers for authenticating through Cloudflare gateway.

    Returns:
        Dictionary of headers to include in requests
    """
    headers = {}

    # CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET are used for service tokens
    cf_client_id = os.getenv("CF_ACCESS_CLIENT_ID")
    cf_client_secret = os.getenv("CF_ACCESS_CLIENT_SECRET")

    if cf_client_id and cf_client_secret:
        headers["CF-Access-Client-Id"] = cf_client_id
        headers["CF-Access-Client-Secret"] = cf_client_secret

    return headers


def _detect_environment() -> str:
    """Detect the current environment based on git branch or ENV variable."""
    # Check explicit ENV variable first
    env = os.getenv("INFISICAL_ENV") or os.getenv("ENV")
    if env:
        return env

    # Try to detect from git branch
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        branch = result.stdout.strip()

        # Load branch mapping from config
        config = _load_infisical_config()
        if config and "gitBranchToEnvironmentMapping" in config:
            mapping = config["gitBranchToEnvironmentMapping"]
            return mapping.get(branch, "dev")

        # Default mapping
        if branch == "main":
            return "prod"
        elif branch == "staging":
            return "staging"
        else:
            return "dev"
    except Exception:
        pass

    return "dev"  # Default fallback


def load_secrets_from_infisical_sdk(
    workspace_id: str | None = None,
    environment: str | None = None,
    path: str = "/",
    site_url: str | None = None,
) -> dict[str, str]:
    """Load secrets using Infisical Python SDK.

    Args:
        workspace_id: Infisical workspace/project ID (reads from .infisical.json if not provided)
        environment: Environment name (dev/staging/prod, auto-detected if not provided)
        path: Secret path in Infisical (default: /)
        site_url: Custom Infisical instance URL (reads from .infisical.json if not provided)

    Returns:
        Dictionary of secrets (key-value pairs)
    """
    if not INFISICAL_SDK_AVAILABLE:
        logger.debug("Infisical SDK not available")
        return {}

    # Load config
    config = _load_infisical_config()

    # Get workspace ID
    if not workspace_id:
        if not config or not config.get("workspaceId"):
            logger.debug("No workspace ID configured in .infisical.json")
            return {}
        workspace_id = config["workspaceId"]

    # Get site URL (for self-hosted instances)
    if not site_url and config:
        site_url = config.get("siteUrl")

    # Get environment
    if not environment:
        environment = _detect_environment()

    # Get authentication token
    token = _get_infisical_token()
    if not token:
        logger.debug("No Infisical token found (set INFISICAL_TOKEN or INFISICAL_CLIENT_ID/SECRET)")
        return {}

    try:
        # Get Cloudflare Access headers if needed
        cf_headers = _get_cloudflare_access_headers()

        # Initialize client with access token and custom site URL
        # The newer SDK version (2.x+) uses access_token in ClientSettings
        client_settings = ClientSettings(
            access_token=token,
            site_url=site_url if site_url else None,
        )
        client = InfisicalClient(client_settings)

        # Log Cloudflare Access detection
        if cf_headers and site_url and "williamshome.family" in site_url:
            logger.debug(
                f"Cloudflare Access configured with client ID: {cf_headers.get('CF-Access-Client-Id', 'N/A')[:20]}..."
            )

        # Fetch all secrets using ListSecretsOptions
        secrets = client.listSecrets(
            ListSecretsOptions(
                environment=environment,
                project_id=workspace_id,
                path=path,
            )
        )

        # Convert to dictionary
        result = {}
        for secret in secrets:
            result[secret.secret_key] = secret.secret_value

        instance = site_url if site_url else "cloud"
        logger.info(
            f"Loaded {len(result)} secrets from Infisical {instance} (workspace: {workspace_id}, env: {environment})"
        )
        return result

    except Exception as e:
        logger.warning(f"Failed to load secrets from Infisical SDK: {e}")
        return {}


def load_secrets_from_infisical_cli(
    environment: str | None = None,
    path: str = "/",
) -> dict[str, str]:
    """Load secrets using Infisical CLI.

    The CLI method automatically handles Cloudflare Access tokens through environment
    variables (CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET).

    Args:
        environment: Environment name (dev/staging/prod, auto-detected if not provided)
        path: Secret path in Infisical (default: /)

    Returns:
        Dictionary of secrets (key-value pairs)
    """
    # Check if CLI is installed
    try:
        subprocess.run(
            ["infisical", "--version"],
            capture_output=True,
            check=True,
            timeout=5,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        logger.debug("Infisical CLI not installed")
        return {}

    # Get environment
    if not environment:
        environment = _detect_environment()

    try:
        # Build environment for subprocess (includes Cloudflare Access tokens if present)
        env = os.environ.copy()

        # Use CLI to export secrets as JSON
        # The CLI automatically uses CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET
        # from the environment if they're set
        result = subprocess.run(
            [
                "infisical",
                "secrets",
                "export",
                "--env",
                environment,
                "--path",
                path,
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
            cwd=_get_project_root(),
            env=env,
        )

        secrets = json.loads(result.stdout)
        logger.info(f"Loaded {len(secrets)} secrets from Infisical CLI (env: {environment})")
        return secrets

    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to load secrets from Infisical CLI: {e.stderr}")
        return {}
    except Exception as e:
        logger.warning(f"Failed to load secrets from Infisical CLI: {e}")
        return {}


def load_secrets_from_infisical(
    workspace_id: str | None = None,
    environment: str | None = None,
    path: str = "/",
    prefer_cli: bool = False,
) -> dict[str, str]:
    """Load secrets from Infisical using best available method.

    Priority (unless prefer_cli=True):
    1. Infisical Python SDK (if available and configured)
    2. Infisical CLI (if installed)
    3. Empty dict (fall back to .env file)

    Args:
        workspace_id: Infisical workspace/project ID (for SDK)
        environment: Environment name (auto-detected if not provided)
        path: Secret path in Infisical
        prefer_cli: If True, try CLI before SDK

    Returns:
        Dictionary of secrets (empty if Infisical not available)
    """
    if prefer_cli:
        # Try CLI first
        secrets = load_secrets_from_infisical_cli(environment=environment, path=path)
        if secrets:
            return secrets

        # Fall back to SDK
        secrets = load_secrets_from_infisical_sdk(
            workspace_id=workspace_id,
            environment=environment,
            path=path,
        )
        if secrets:
            return secrets
    else:
        # Try SDK first
        secrets = load_secrets_from_infisical_sdk(
            workspace_id=workspace_id,
            environment=environment,
            path=path,
        )
        if secrets:
            return secrets

        # Fall back to CLI
        secrets = load_secrets_from_infisical_cli(environment=environment, path=path)
        if secrets:
            return secrets

    logger.debug("No secrets loaded from Infisical, will fall back to .env file")
    return {}


def inject_secrets_into_env(secrets: dict[str, str], override: bool = False) -> int:
    """Inject secrets into os.environ.

    Args:
        secrets: Dictionary of secrets to inject
        override: If True, override existing environment variables

    Returns:
        Number of secrets injected
    """
    count = 0
    for key, value in secrets.items():
        if override or key not in os.environ:
            os.environ[key] = value
            count += 1

    return count
