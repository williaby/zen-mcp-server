"""
Band-based Model Selector

Centralized model selection using the sophisticated band configuration system.
Provides future-proof, data-driven model selection that automatically adapts
when band criteria change.
"""

import json
import logging
import os
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    """Model performance and cost metrics."""

    name: str
    provider: str
    tier: str
    cost_input: float
    cost_output: float
    org_level: str
    specialization: str
    role: str
    humaneval_score: float
    swe_bench_score: float
    context_window: int
    rank: int


class BandSelector:
    """Intelligent model selector using centralized band configurations."""

    def __init__(self, bands_config_path: str = None, models_csv_path: str = None):
        self.bands_config_path = bands_config_path or self._get_default_bands_config_path()
        self.models_csv_path = models_csv_path or self._get_default_models_csv_path()
        self.bands_config = None
        self.models_df = None
        self._load_configurations()

    def _get_default_bands_config_path(self) -> str:
        """Get default bands configuration path."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(base_dir, "docs", "models", "bands_config.json")

    def _get_default_models_csv_path(self) -> str:
        """Get default models CSV path."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(base_dir, "docs", "models", "models.csv")

    def _load_configurations(self):
        """Load band configuration and models data."""
        try:
            # Load bands configuration
            if os.path.exists(self.bands_config_path):
                with open(self.bands_config_path) as f:
                    self.bands_config = json.load(f)
                logger.debug(f"Loaded bands config from {self.bands_config_path}")
            else:
                logger.error(f"Bands config not found: {self.bands_config_path}")
                self.bands_config = self._get_fallback_bands_config()

            # Load models CSV - try pandas first, fall back to csv module
            if os.path.exists(self.models_csv_path):
                try:
                    self.models_df = pd.read_csv(self.models_csv_path)
                    logger.debug(f"Loaded {len(self.models_df)} models from CSV with pandas")
                except Exception as e:
                    logger.warning(f"Pandas failed, trying csv module: {e}")
                    self.models_df = self._load_csv_fallback()
            else:
                logger.error(f"Models CSV not found: {self.models_csv_path}")
                self.models_df = self._get_fallback_models_df()

        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
            self.bands_config = self._get_fallback_bands_config()
            self.models_df = self._get_fallback_models_df()

    def get_models_by_org_level(self, org_level: str, limit: int = 10, role: str = None) -> list[str]:
        """Get models filtered by organizational level using band criteria."""
        try:
            # Get org level criteria from bands config
            org_bands = self.bands_config.get("org_level_assignment_bands", {})

            if org_level == "startup":
                band_key = "junior"
            elif org_level == "scaleup":
                band_key = "senior"
            else:  # enterprise
                band_key = "executive"

            criteria = org_bands.get(band_key, {})

            # Apply band criteria filters
            filtered_df = self._apply_org_level_criteria(self.models_df, criteria)

            # Apply role specialization if specified
            if role:
                filtered_df = self._apply_role_specialization(filtered_df, role)

            # Sort by performance metrics
            filtered_df = self._sort_by_performance(filtered_df)

            # Return top N model names
            return filtered_df.head(limit)["model"].tolist()

        except Exception as e:
            logger.error(f"Error in get_models_by_org_level (org_level={org_level}, limit={limit}, role={role}): {e}")
            return self._get_fallback_models(org_level, limit)

    def get_models_by_cost_tier(self, tier: str, limit: int = 5) -> list[str]:
        """Get models by cost tier band."""
        try:
            cost_bands = self.bands_config.get("cost_tier_bands", {})
            criteria = cost_bands.get(tier, {})

            filtered_df = self._apply_cost_criteria(self.models_df, criteria)
            filtered_df = self._sort_by_performance(filtered_df)

            return filtered_df.head(limit)["model"].tolist()

        except Exception as e:
            logger.error(f"Error in get_models_by_cost_tier (tier={tier}, limit={limit}): {e}")
            return self._get_fallback_models("startup", limit)

    def get_models_by_role(self, role: str, org_level: str = "senior", limit: int = 3) -> list[str]:
        """Get models optimized for specific professional role."""
        try:
            # Get role assignment bands
            self.bands_config.get("role_assignment_bands", {})

            # Map role to band category
            role_mapping = self._get_role_to_band_mapping()
            role_mapping.get(role, "validation_roles")

            # Get org level models first
            org_models = self.get_models_by_org_level(org_level, limit=20)

            # Filter by role specialization
            role_df = self.models_df[self.models_df["model"].isin(org_models)]
            role_df = self._apply_role_specialization(role_df, role)
            role_df = self._sort_by_performance(role_df)

            return role_df.head(limit)["model"].tolist()

        except Exception as e:
            logger.error(f"Error in get_models_by_role (role={role}, org_level={org_level}, limit={limit}): {e}")
            return self._get_fallback_models(org_level, limit)

    def _apply_org_level_criteria(self, df: pd.DataFrame, criteria: dict) -> pd.DataFrame:
        """Apply organizational level criteria from bands config."""
        filtered_df = df.copy()

        # Apply cost criteria (skip if unlimited=True is set for this org level)
        cost_criteria = criteria.get("cost_criteria", {})
        if not cost_criteria.get("unlimited") and "max_input_cost" in cost_criteria:
            filtered_df = filtered_df[filtered_df["input_cost"] <= cost_criteria["max_input_cost"]]

        # Apply performance criteria
        perf_criteria = criteria.get("performance_criteria", {})
        if "min_humaneval" in perf_criteria:
            filtered_df = filtered_df[filtered_df["humaneval_score"] >= perf_criteria["min_humaneval"]]

        # Apply context criteria
        context_criteria = criteria.get("context_criteria", {})
        if "min_context" in context_criteria:
            # Convert context values like "131K" to numeric (131000)
            def convert_context_to_numeric(value):
                if pd.isna(value):
                    return 0
                if isinstance(value, str):
                    value = value.strip().upper()
                    if value.endswith("K"):
                        try:
                            return float(value[:-1]) * 1000
                        except ValueError:
                            return 0
                    elif value.endswith("M"):
                        try:
                            return float(value[:-1]) * 1000000
                        except ValueError:
                            return 0
                    else:
                        try:
                            return float(value)
                        except ValueError:
                            return 0
                return float(value) if value else 0

            filtered_df["context_numeric"] = filtered_df["context"].apply(convert_context_to_numeric)
            filtered_df = filtered_df[filtered_df["context_numeric"] >= context_criteria["min_context"]]

        return filtered_df

    def _apply_cost_criteria(self, df: pd.DataFrame, criteria: dict) -> pd.DataFrame:
        """Apply cost tier criteria.

        Uses explicit index selection (iterrows + df.loc) instead of boolean
        array indexing to avoid the pandas 2.3/numpy 2.2 _NoValueType bug on
        Python 3.10 that causes TypeError in df[bool_mask] for all column dtypes.
        """
        max_cost = criteria.get("max_cost")
        min_cost = criteria.get("min_cost")

        if max_cost is None and min_cost is None:
            return df.copy()

        keep_indices = []
        for idx, row in df.iterrows():
            try:
                cost = float(row["input_cost"])
                out_cost = float(row["output_cost"])
            except (ValueError, TypeError, KeyError):
                continue

            if max_cost is not None:
                if max_cost == 0.0:
                    # Free tier: both input and output cost must be exactly zero
                    if cost != 0.0 or out_cost != 0.0:
                        continue
                elif cost > max_cost:
                    continue

            if min_cost is not None and cost < min_cost:
                continue

            keep_indices.append(idx)

        return df.loc[keep_indices].copy() if keep_indices else df.iloc[0:0].copy()

    def _apply_role_specialization(self, df: pd.DataFrame, role: str) -> pd.DataFrame:
        """Apply role-based specialization filtering."""
        # Define role to specialization mapping
        role_specializations = {
            "code_reviewer": ["coding", "general"],
            "security_checker": ["security", "reasoning"],
            "technical_validator": ["general", "debugging"],
            "senior_developer": ["coding", "general"],
            "system_architect": ["general", "reasoning"],
            "devops_engineer": ["general", "debugging"],
            "lead_architect": ["reasoning", "general"],
            "technical_director": ["general", "reasoning"],
        }

        preferred_specs = role_specializations.get(role, ["general"])

        # Prioritize models with matching specializations
        role_df = df.copy()
        role_df["spec_match"] = role_df["specialization"].apply(lambda x: 1 if x in preferred_specs else 0)

        # Sort by specialization match, then performance
        role_df = role_df.sort_values(["spec_match", "humaneval_score"], ascending=[False, False])

        return role_df

    def _sort_by_performance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sort models by performance metrics (numeric columns only).

        Note: "context" is excluded because it is stored as a string (e.g. "131K")
        in models.csv. Sorting on a string column triggers a TypeError with
        pandas 2.3/numpy 2.2 on Python 3.10 that causes the broad except handler
        in callers to silently fall back to free-tier models.
        """
        return df.sort_values(["humaneval_score", "swe_bench_score"], ascending=[False, False])

    def _get_role_to_band_mapping(self) -> dict[str, str]:
        """Get role to band category mapping."""
        return {
            "code_reviewer": "technical_roles",
            "security_checker": "analysis_roles",
            "technical_validator": "validation_roles",
            "senior_developer": "technical_roles",
            "system_architect": "architecture_roles",
            "devops_engineer": "technical_roles",
            "lead_architect": "architecture_roles",
            "technical_director": "architecture_roles",
        }

    def _get_fallback_bands_config(self) -> dict:
        """Fallback bands configuration."""
        return {
            "org_level_assignment_bands": {
                "junior": {
                    "cost_criteria": {"max_input_cost": 1.0},
                    "performance_criteria": {"min_humaneval": 60.0},
                    "context_criteria": {"min_context": 32000},
                },
                "senior": {
                    "cost_criteria": {"max_input_cost": 10.0},
                    "performance_criteria": {"min_humaneval": 70.0},
                    "context_criteria": {"min_context": 65000},
                },
                "executive": {
                    "cost_criteria": {"unlimited": True},
                    "performance_criteria": {"min_humaneval": 80.0},
                    "context_criteria": {"min_context": 128000},
                },
            },
            "cost_tier_bands": {
                "free": {"max_cost": 0.0},
                "economy": {"min_cost": 0.01, "max_cost": 1.0},
                "value": {"min_cost": 1.01, "max_cost": 10.0},
                "premium": {"min_cost": 10.01},
            },
        }

    def _get_fallback_models_df(self) -> pd.DataFrame:
        """Fallback models dataframe."""
        fallback_data = [
            {
                "model": "deepseek/deepseek-chat:free",
                "provider": "deepseek",
                "input_cost": 0.0,
                "output_cost": 0.0,
                "humaneval_score": 75.0,
                "swe_bench_score": 65.0,
                "context": 131000,
                "specialization": "general",
            },
            {
                "model": "meta-llama/llama-3.3-70b-instruct:free",
                "provider": "meta",
                "input_cost": 0.0,
                "output_cost": 0.0,
                "humaneval_score": 80.0,
                "swe_bench_score": 68.0,
                "context": 131000,
                "specialization": "general",
            },
            {
                "model": "google/gemini-2.5-flash",
                "provider": "google",
                "input_cost": 0.075,
                "output_cost": 0.30,
                "humaneval_score": 78.0,
                "swe_bench_score": 65.0,
                "context": 1048000,
                "specialization": "general",
            },
            {
                "model": "anthropic/claude-sonnet-4",
                "provider": "anthropic",
                "input_cost": 3.0,
                "output_cost": 15.0,
                "humaneval_score": 85.0,
                "swe_bench_score": 72.0,
                "context": 200000,
                "specialization": "reasoning",
            },
            {
                "model": "anthropic/claude-opus-4.6",
                "provider": "anthropic",
                "input_cost": 15.0,
                "output_cost": 75.0,
                "humaneval_score": 88.0,
                "swe_bench_score": 78.0,
                "context": 200000,
                "specialization": "reasoning",
            },
        ]
        return pd.DataFrame(fallback_data)

    def _get_fallback_models(self, org_level: str, limit: int) -> list[str]:
        """Get fallback model names."""
        if org_level == "startup":
            models = [
                "deepseek/deepseek-chat:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "qwen/qwen-2.5-coder-32b-instruct:free",
            ]
        elif org_level == "scaleup":
            models = [
                "deepseek/deepseek-chat:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "google/gemini-2.5-flash",
                "openai/gpt-5-mini",
                "anthropic/claude-sonnet-4",
            ]
        else:  # enterprise
            models = [
                "anthropic/claude-opus-4.6",
                "openai/gpt-5",
                "google/gemini-3-pro-preview",
                "anthropic/claude-sonnet-4",
                "openai/gpt-5-chat",
                "mistralai/mistral-large-2411",
                "google/gemini-2.5-flash",
                "deepseek/deepseek-r1-0528",
            ]

        return models[:limit]

    def _load_csv_fallback(self) -> pd.DataFrame:
        """Load CSV using standard csv module when pandas fails."""
        try:
            import csv

            data = []
            with open(self.models_csv_path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert numeric fields
                    try:
                        row["input_cost"] = float(row.get("input_cost", 0))
                        row["output_cost"] = float(row.get("output_cost", 0))
                        row["humaneval_score"] = float(row.get("humaneval_score", 70))
                        row["swe_bench_score"] = float(row.get("swe_bench_score", 60))
                        row["context"] = int(row.get("context", 65000))
                        row["rank"] = int(row.get("rank", 999))
                    except (ValueError, TypeError):
                        # Use defaults for invalid data
                        row["input_cost"] = 0.0
                        row["output_cost"] = 0.0
                        row["humaneval_score"] = 70.0
                        row["swe_bench_score"] = 60.0
                        row["context"] = 65000
                        row["rank"] = 999
                    data.append(row)

            df = pd.DataFrame(data)
            logger.debug(f"Loaded {len(df)} models using csv fallback")
            return df
        except Exception as e:
            logger.error(f"CSV fallback failed: {e}")
            return self._get_fallback_models_df()
