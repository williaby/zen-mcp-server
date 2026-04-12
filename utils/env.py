"""Centralized environment variable access for PAL MCP Server."""

from __future__ import annotations

import os
from collections.abc import Mapping
from contextlib import contextmanager
from pathlib import Path

try:
    from dotenv import dotenv_values, load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    dotenv_values = None  # type: ignore[assignment]
    load_dotenv = None  # type: ignore[assignment]

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"

_DOTENV_VALUES: dict[str, str | None] = {}
_FORCE_ENV_OVERRIDE = False
_INFISICAL_LOADED = False


def _read_dotenv_values() -> dict[str, str | None]:
    if dotenv_values is not None and _ENV_PATH.exists():
        loaded = dotenv_values(_ENV_PATH)
        return dict(loaded)
    return {}


def _compute_force_override(values: Mapping[str, str | None]) -> bool:
    raw = (values.get("PAL_MCP_FORCE_ENV_OVERRIDE") or "false").strip().lower()
    return raw == "true"


def reload_env(dotenv_mapping: Mapping[str, str | None] | None = None, use_infisical: bool = True) -> None:
    """Reload .env values and recompute override semantics.

    Args:
        dotenv_mapping: Optional mapping used instead of reading the .env file.
            Intended for tests; when provided, load_dotenv is not invoked.
        use_infisical: If True, attempt to load secrets from Infisical before .env file
    """

    global _DOTENV_VALUES, _FORCE_ENV_OVERRIDE, _INFISICAL_LOADED

    if dotenv_mapping is not None:
        _DOTENV_VALUES = dict(dotenv_mapping)
        _FORCE_ENV_OVERRIDE = _compute_force_override(_DOTENV_VALUES)
        return

    # Try to load from Infisical first (if enabled and available)
    if use_infisical and not _INFISICAL_LOADED:
        try:
            from utils.infisical import inject_secrets_into_env, load_secrets_from_infisical

            secrets = load_secrets_from_infisical()
            if secrets:
                # Inject secrets into environment (don't override existing vars)
                inject_secrets_into_env(secrets, override=False)
                # Also store in _DOTENV_VALUES for consistent access
                _DOTENV_VALUES.update(secrets)
            # Mark as loaded regardless of result to prevent repeated subprocess
            # calls in environments where Infisical is not configured.
            _INFISICAL_LOADED = True
        except ImportError:
            # Infisical not installed, fall back to .env
            _INFISICAL_LOADED = True
        except Exception as e:
            # Log error but continue with .env fallback
            import logging

            logging.getLogger(__name__).warning(f"Failed to load secrets from Infisical: {e}")
            _INFISICAL_LOADED = True

    # Load from .env file (as fallback or supplement)
    dotenv_values_from_file = _read_dotenv_values()
    # Merge with Infisical values (Infisical takes precedence)
    for key, value in dotenv_values_from_file.items():
        if key not in _DOTENV_VALUES:
            _DOTENV_VALUES[key] = value

    _FORCE_ENV_OVERRIDE = _compute_force_override(_DOTENV_VALUES)

    if load_dotenv is not None and _ENV_PATH.exists():
        load_dotenv(dotenv_path=_ENV_PATH, override=_FORCE_ENV_OVERRIDE)


reload_env()


def env_override_enabled() -> bool:
    """Return True when PAL_MCP_FORCE_ENV_OVERRIDE is enabled via the .env file."""

    return _FORCE_ENV_OVERRIDE


def get_env(key: str, default: str | None = None) -> str | None:
    """Retrieve environment variables respecting PAL_MCP_FORCE_ENV_OVERRIDE."""

    if env_override_enabled():
        if key in _DOTENV_VALUES:
            value = _DOTENV_VALUES[key]
            return value if value is not None else default
        return default

    return os.getenv(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """Boolean helper that respects override semantics."""

    raw_default = "true" if default else "false"
    raw_value = get_env(key, raw_default)
    return (raw_value or raw_default).strip().lower() == "true"


def get_all_env() -> dict[str, str | None]:
    """Expose the loaded .env mapping for diagnostics/logging."""

    return dict(_DOTENV_VALUES)


@contextmanager
def suppress_env_vars(*names: str):
    """Temporarily remove environment variables during the context.

    Args:
        names: Environment variable names to remove. Empty or falsy names are ignored.
    """

    removed: dict[str, str] = {}
    try:
        for name in names:
            if not name:
                continue
            if name in os.environ:
                removed[name] = os.environ[name]
                del os.environ[name]
        yield
    finally:
        for name, value in removed.items():
            os.environ[name] = value
