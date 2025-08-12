"""
Dynamic Model Selector for Consensus Tools

This module provides intelligent model selection by reading the available-models.md
file and selecting models based on price tiers, specializations, and quality rankings.

Eliminates hardcoded model lists by dynamically querying the current model configuration.
"""

from __future__ import annotations

import csv
import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import jsonschema
    SCHEMA_VALIDATION_AVAILABLE = True
except ImportError:
    SCHEMA_VALIDATION_AVAILABLE = False
    logger.warning("jsonschema package not available - schema validation disabled")

logger = logging.getLogger(__name__)

# Path to the master models data file and bands configuration
MODELS_CSV_PATH = Path(__file__).parent.parent.parent / "docs" / "models" / "models.csv"
BANDS_CONFIG_PATH = Path(__file__).parent.parent.parent / "docs" / "models" / "bands_config.json"
SCHEMA_PATH = Path(__file__).parent.parent.parent / "docs" / "models" / "models_schema.json"


class DynamicModelSelector:
    """
    Dynamic model selector that reads from available-models.md and selects
    models based on price tiers, specializations, and quality rankings.
    """
    
    # Class-level cache for models data
    _cached_models_data = None
    _cached_bands_config = None
    _cache_timestamp = None
    _csv_file_mtime = None
    _bands_file_mtime = None
    
    def __init__(self):
        self.models_data = []
        self.parsed_models = {}
        self.bands_config = {}
        self.schema = None
        self._load_schema()
        self._load_cached_data()
        
        # Auto-detect and apply any band/tier changes on initialization
        self._auto_detect_band_changes()
    
    def _load_schema(self):
        """Load JSON schema for models validation"""
        if not SCHEMA_VALIDATION_AVAILABLE:
            logger.info("Schema validation disabled - jsonschema package not available")
            return
            
        try:
            if not SCHEMA_PATH.exists():
                logger.warning(f"Schema file not found: {SCHEMA_PATH}")
                return
            
            with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            
            logger.info("Loaded JSON schema for models validation")
            
        except Exception as e:
            logger.error(f"Failed to load JSON schema: {e}")
            self.schema = None
    
    def _load_cached_data(self):
        """Load data using cache if files haven't changed"""
        try:
            # Check if we need to reload data
            csv_mtime = MODELS_CSV_PATH.stat().st_mtime if MODELS_CSV_PATH.exists() else 0
            bands_mtime = BANDS_CONFIG_PATH.stat().st_mtime if BANDS_CONFIG_PATH.exists() else 0
            
            # Use cache if files haven't changed
            if (DynamicModelSelector._cached_models_data and 
                DynamicModelSelector._csv_file_mtime == csv_mtime and
                DynamicModelSelector._bands_file_mtime == bands_mtime):
                
                logger.debug("Using cached model data (files unchanged)")
                self.models_data = DynamicModelSelector._cached_models_data
                self.bands_config = DynamicModelSelector._cached_bands_config
                self.parsed_models = {m['name']: m for m in self.models_data}
                return
            
            # Need to reload data
            logger.debug("Cache miss or files changed, reloading model data")
            self._load_bands_config()
            self._parse_models_csv()
            
            # Update cache
            DynamicModelSelector._cached_models_data = self.models_data
            DynamicModelSelector._cached_bands_config = self.bands_config
            DynamicModelSelector._cache_timestamp = time.time()
            DynamicModelSelector._csv_file_mtime = csv_mtime
            DynamicModelSelector._bands_file_mtime = bands_mtime
            
            logger.debug(f"Updated cache with {len(self.models_data)} models")
            
        except Exception as e:
            logger.error(f"Error in cached data loading: {e}")
            # Fallback to normal loading
            self._load_bands_config()
            self._parse_models_csv()
    
    def _validate_models_data(self, models_list: List[Dict]) -> bool:
        """Validate models data against JSON schema"""
        if not SCHEMA_VALIDATION_AVAILABLE or not self.schema:
            logger.debug("Schema validation skipped - not available or not loaded")
            return True
        
        try:
            # Wrap models list in schema-expected format
            data_to_validate = {"models": models_list}
            jsonschema.validate(data_to_validate, self.schema)
            logger.info(f"Schema validation passed for {len(models_list)} models")
            return True
            
        except jsonschema.ValidationError as e:
            logger.error(f"Schema validation failed: {e.message}")
            logger.error(f"Failed at path: {' -> '.join(str(p) for p in e.absolute_path)}")
            logger.error(f"Invalid data: {e.instance}")
            return False
            
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return False
    
    def _load_bands_config(self):
        """Load quantitative scoring bands configuration"""
        try:
            if not BANDS_CONFIG_PATH.exists():
                logger.warning(f"Bands config file not found: {BANDS_CONFIG_PATH}")
                # Use default bands if config file is missing
                self.bands_config = self._get_default_bands()
                return
            
            with open(BANDS_CONFIG_PATH, 'r', encoding='utf-8') as f:
                self.bands_config = json.load(f)
            
            logger.info("Loaded quantitative scoring bands configuration")
            
        except Exception as e:
            logger.error(f"Failed to load bands configuration: {e}")
            self.bands_config = self._get_default_bands()
    
    def _get_default_bands(self) -> dict:
        """Fallback default bands configuration"""
        return {
            "context_window_bands": {
                "small": {"max_tokens": 131000},
                "standard": {"min_tokens": 132000, "max_tokens": 400000},
                "large": {"min_tokens": 400001}
            },
            "cost_tier_bands": {
                "Free": {"max_cost": 0.0},
                "Economy": {"min_cost": 0.01, "max_cost": 0.99},
                "Value": {"min_cost": 1.0, "max_cost": 3.0},
                "Premium": {"min_cost": 3.01}
            }
        }
    
    def _parse_models_csv(self):
        """Parse the CSV file containing model data"""
        try:
            temp_models_data = []
            
            with open(MODELS_CSV_PATH, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    try:
                        parsed_model = self._parse_csv_row(row)
                        if parsed_model:
                            temp_models_data.append(parsed_model)
                    except Exception as e:
                        logger.debug(f"Failed to parse CSV row: {row.get('model', 'unknown')}... Error: {e}")
                        continue
            
            # Validate parsed data against schema
            if self._validate_models_data(temp_models_data):
                self.models_data = temp_models_data
                # Rebuild parsed_models dict
                self.parsed_models = {m['name']: m for m in self.models_data}
                logger.info(f"Successfully loaded and validated {len(self.models_data)} models")
            else:
                logger.warning("Schema validation failed - using data without validation")
                self.models_data = temp_models_data
                self.parsed_models = {m['name']: m for m in self.models_data}
                        
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
    
    def _parse_csv_row(self, row: dict) -> Optional[Dict]:
        """Parse a single row from the CSV file"""
        try:
            rank = int(row['rank'])
            model_name = row['model']
            tier = row['tier']
            status = row['status']
            context = row['context']
            input_cost = row['input_cost']
            output_cost = row['output_cost']
            org_level = row['org_level'].lower()
            specialization = row['specialization'].lower()
            role = row['role'].lower()
            strength = row['strength'].lower()
            
            # Parse input cost (extract numeric value)
            input_cost_numeric = self._parse_cost(input_cost)
            output_cost_numeric = self._parse_cost(output_cost)
            
            # Parse context window
            context_numeric = self._parse_context(context)
            
            model_data = {
                'rank': rank,
                'name': model_name,
                'tier': tier,
                'status': status,
                'context_window': context_numeric,
                'input_cost': input_cost_numeric,
                'output_cost': output_cost_numeric,
                'org_level': org_level,
                'specialization': specialization,
                'role': role,
                'strength': strength,
                'price_tier': self._determine_price_tier(input_cost_numeric)
            }
            
            return model_data
            
        except (ValueError, KeyError) as e:
            logger.debug(f"Error parsing CSV row for model {row.get('model', 'unknown')}: {e}")
            return None
    
    def _parse_cost(self, cost_str: str) -> float:
        """Parse cost string to numeric value ($/M tokens)"""
        if "$0" in cost_str or "FREE" in cost_str.upper():
            return 0.0
        
        # Extract numeric value from strings like "$2/M", "$0.075/M", "~$0.15/M"
        match = re.search(r'[\$~]*(\d+\.?\d*)', cost_str)
        if match:
            return float(match.group(1))
        
        return 999.0  # Default high cost if can't parse
    
    def _parse_context(self, context_str: str) -> int:
        """Parse context window to numeric value (tokens)"""
        # Extract numeric value and convert units
        match = re.search(r'(\d+\.?\d*)([KM]?)', context_str)
        if match:
            value = float(match.group(1))
            unit = match.group(2)
            
            if unit == 'K':
                return int(value * 1000)
            elif unit == 'M':
                return int(value * 1000000)
            else:
                return int(value)
        
        return 32000  # Default context window
    
    def _determine_price_tier(self, input_cost: float) -> str:
        """Determine price tier based on input cost using quantitative bands"""
        return self.get_cost_tier_band(input_cost).lower()
    
    def _determine_specializations(self, model_name: str, strengths: str) -> List[str]:
        """Determine model specializations based on name and strengths"""
        text = f"{model_name} {strengths}".lower()
        specializations = []
        
        for spec_type, keywords in SPECIALIZATIONS.items():
            if any(keyword in text for keyword in keywords):
                specializations.append(spec_type)
        
        if not specializations:
            specializations.append("general")
        
        return specializations
    
    def get_models_by_tier(self, price_tier: str) -> List[Dict]:
        """Get all models in a specific price tier, sorted by rank"""
        models = [m for m in self.models_data if m['price_tier'] == price_tier]
        return sorted(models, key=lambda x: x['rank'])
    
    def get_models_by_specialization(self, specialization: str, price_tier: str = None) -> List[Dict]:
        """Get models with specific specialization, optionally filtered by price tier"""
        models = [m for m in self.models_data if specialization in m['specializations']]
        
        if price_tier:
            models = [m for m in models if m['price_tier'] == price_tier]
        
        return sorted(models, key=lambda x: x['rank'])
    
    def get_best_model_for_role(self, role: str, price_tier: str) -> Optional[str]:
        """Get the best model for a specific role within a price tier"""
        
        # Map roles to specializations
        role_specializations = {
            "code_reviewer": "coding",
            "security_analyst": "reasoning", 
            "technical_evaluator": "general",
            "senior_developer": "coding",
            "system_architect": "reasoning",
            "devops_engineer": "general",
            "lead_architect": "reasoning",
            "technical_director": "general",
            "security_chief": "reasoning",
            "research_lead": "reasoning",
            "risk_analysis_specialist": "reasoning"
        }
        
        specialization = role_specializations.get(role.lower(), "general")
        models = self.get_models_by_specialization(specialization, price_tier)
        
        if models:
            return models[0]['name']  # Return best ranked model
        
        # Fallback to any model in price tier
        tier_models = self.get_models_by_tier(price_tier)
        if tier_models:
            return tier_models[0]['name']
        
        return None
    
    def get_context_window_band(self, context_tokens: int) -> str:
        """Determine context window band based on centralized band configuration"""
        bands = self.bands_config.get("context_window_bands", {})
        
        # Skip metadata fields
        band_order = ["compact", "standard", "extended", "large"]
        
        for band_name in band_order:
            if band_name not in bands:
                continue
                
            band_config = bands[band_name]
            
            # Skip metadata fields
            if not isinstance(band_config, dict) or 'description' not in band_config:
                continue
            
            min_tokens = band_config.get("min_tokens", 0)
            max_tokens = band_config.get("max_tokens", float('inf'))
            
            if min_tokens <= context_tokens <= max_tokens:
                return band_name
        
        return "standard"  # default fallback
    
    def reassign_models_to_bands(self) -> Dict[str, List[str]]:
        """
        Reassign all models to context window bands based on current band configuration.
        This is called automatically when band ranges are updated.
        
        Returns:
            Dict mapping band names to lists of model names in each band
        """
        band_assignments = {
            "compact": [],
            "standard": [], 
            "extended": [],
            "large": []
        }
        
        logger.info("Reassigning models to context window bands based on current configuration")
        
        for model in self.models_data:
            context_tokens = model.get('context_window', 0)
            band = self.get_context_window_band(context_tokens)
            
            if band in band_assignments:
                band_assignments[band].append(model['name'])
                logger.debug(f"Assigned {model['name']} ({context_tokens:,} tokens) to {band} band")
        
        # Log the reassignment summary
        for band_name, models in band_assignments.items():
            logger.info(f"{band_name.title()} band: {len(models)} models - {models}")
        
        return band_assignments
    
    def update_models_csv_with_new_bands(self, band_assignments: Dict[str, List[str]]) -> None:
        """
        Update the models.csv file with new context window band assignments.
        This automatically updates the 'context_band' column when ranges change.
        """
        try:
            import csv
            import tempfile
            import shutil
            
            # Read current CSV data
            rows = []
            with open(MODELS_CSV_PATH, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                
                # Add context_band column if it doesn't exist
                if 'context_band' not in fieldnames:
                    fieldnames = list(fieldnames) + ['context_band']
                
                for row in reader:
                    # Find which band this model belongs to
                    model_name = row['model']
                    assigned_band = None
                    
                    for band_name, models in band_assignments.items():
                        if model_name in models:
                            assigned_band = band_name
                            break
                    
                    row['context_band'] = assigned_band or 'standard'
                    rows.append(row)
            
            # Write updated CSV to temporary file first
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
            try:
                writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
                temp_file.close()
                
                # Replace original file with updated version
                shutil.move(temp_file.name, MODELS_CSV_PATH)
                logger.info(f"Updated models.csv with new context window band assignments")
                
            except Exception as e:
                # Clean up temp file on error
                import os
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                raise e
                
        except Exception as e:
            logger.error(f"Failed to update models.csv with new band assignments: {e}")
    
    def detect_and_apply_band_changes(self) -> bool:
        """
        Detect if context window bands have changed and automatically reassign models.
        
        Returns:
            True if changes were detected and applied, False otherwise
        """
        try:
            # Get current band assignments
            new_assignments = self.reassign_models_to_bands()
            
            # Check if we have a previous assignment record
            assignment_cache_file = MODELS_CSV_PATH.parent / "band_assignments_cache.json"
            
            if assignment_cache_file.exists():
                import json
                with open(assignment_cache_file, 'r') as f:
                    previous_assignments = json.load(f)
                
                # Compare with previous assignments
                if previous_assignments != new_assignments:
                    logger.info("Context window band changes detected - reassigning models")
                    
                    # Update the CSV file
                    self.update_models_csv_with_new_bands(new_assignments)
                    
                    # Update the cache
                    with open(assignment_cache_file, 'w') as f:
                        json.dump(new_assignments, f, indent=2)
                    
                    return True
                else:
                    logger.debug("No context window band changes detected")
                    return False
            else:
                # First time - create cache
                import json
                with open(assignment_cache_file, 'w') as f:
                    json.dump(new_assignments, f, indent=2)
                
                logger.info("Created initial context window band assignment cache")
                return True
                
        except Exception as e:
            logger.error(f"Failed to detect/apply band changes: {e}")
            return False
    
    def get_cost_tier_band(self, input_cost: float) -> str:
        """Determine cost tier band based on centralized band configuration"""
        bands = self.bands_config.get("cost_tier_bands", {})
        
        # Skip metadata fields
        band_order = ["free", "economy", "value", "premium"]
        
        for band_name in band_order:
            if band_name not in bands:
                continue
                
            band_config = bands[band_name]
            
            # Skip metadata fields
            if not isinstance(band_config, dict) or 'description' not in band_config:
                continue
            
            min_cost = band_config.get("min_cost", 0.0)
            max_cost = band_config.get("max_cost", float('inf'))
            
            if min_cost <= input_cost <= max_cost:
                return band_name
        
        return "economy"  # default fallback
    
    def reassign_models_to_cost_tiers(self) -> Dict[str, List[str]]:
        """
        Reassign all models to cost tier bands based on current band configuration.
        This is called automatically when cost tier ranges are updated.
        
        Returns:
            Dict mapping cost tier names to lists of model names in each tier
        """
        tier_assignments = {
            "free": [],
            "economy": [],
            "value": [],
            "premium": []
        }
        
        logger.info("Reassigning models to cost tier bands based on current configuration")
        
        for model in self.models_data:
            input_cost = model.get('input_cost', 0.0)
            tier = self.get_cost_tier_band(input_cost)
            
            if tier in tier_assignments:
                tier_assignments[tier].append(model['name'])
                logger.debug(f"Assigned {model['name']} (${input_cost}/M tokens) to {tier} tier")
        
        # Log the reassignment summary
        for tier_name, models in tier_assignments.items():
            logger.info(f"{tier_name.title()} tier: {len(models)} models - {models}")
        
        return tier_assignments
    
    def update_models_csv_with_new_cost_tiers(self, tier_assignments: Dict[str, List[str]]) -> None:
        """
        Update the models.csv file with new cost tier assignments.
        This automatically updates the 'cost_tier' column when ranges change.
        """
        try:
            import csv
            import tempfile
            import shutil
            
            # Read current CSV data
            rows = []
            with open(MODELS_CSV_PATH, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                
                # Add cost_tier column if it doesn't exist
                if 'cost_tier' not in fieldnames:
                    fieldnames = list(fieldnames) + ['cost_tier']
                
                for row in reader:
                    # Find which tier this model belongs to
                    model_name = row['model']
                    assigned_tier = None
                    
                    for tier_name, models in tier_assignments.items():
                        if model_name in models:
                            assigned_tier = tier_name
                            break
                    
                    row['cost_tier'] = assigned_tier or 'economy'
                    rows.append(row)
            
            # Write updated CSV to temporary file first
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
            try:
                writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
                temp_file.close()
                
                # Replace original file with updated version
                shutil.move(temp_file.name, MODELS_CSV_PATH)
                logger.info(f"Updated models.csv with new cost tier assignments")
                
            except Exception as e:
                # Clean up temp file on error
                import os
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                raise e
                
        except Exception as e:
            logger.error(f"Failed to update models.csv with new cost tier assignments: {e}")
    
    def detect_and_apply_cost_tier_changes(self) -> bool:
        """
        Detect if cost tier bands have changed and automatically reassign models.
        
        Returns:
            True if changes were detected and applied, False otherwise
        """
        try:
            # Get current tier assignments
            new_assignments = self.reassign_models_to_cost_tiers()
            
            # Check if we have a previous assignment record
            assignment_cache_file = MODELS_CSV_PATH.parent / "cost_tier_assignments_cache.json"
            
            if assignment_cache_file.exists():
                import json
                with open(assignment_cache_file, 'r') as f:
                    previous_assignments = json.load(f)
                
                # Compare with previous assignments
                if previous_assignments != new_assignments:
                    logger.info("Cost tier band changes detected - reassigning models")
                    
                    # Update the CSV file
                    self.update_models_csv_with_new_cost_tiers(new_assignments)
                    
                    # Update the cache
                    with open(assignment_cache_file, 'w') as f:
                        json.dump(new_assignments, f, indent=2)
                    
                    return True
                else:
                    logger.debug("No cost tier band changes detected")
                    return False
            else:
                # First time - create cache
                import json
                with open(assignment_cache_file, 'w') as f:
                    json.dump(new_assignments, f, indent=2)
                
                logger.info("Created initial cost tier assignment cache")
                return True
                
        except Exception as e:
            logger.error(f"Failed to detect/apply cost tier changes: {e}")
            return False
    
    def _auto_detect_band_changes(self) -> None:
        """
        Automatically detect and apply context window band and cost tier changes.
        Called on initialization to ensure models are assigned to current band definitions.
        """
        try:
            logger.debug("Auto-detecting band/tier configuration changes")
            
            # Check for context window band changes
            context_changes = self.detect_and_apply_band_changes()
            
            # Check for cost tier band changes
            cost_changes = self.detect_and_apply_cost_tier_changes()
            
            if context_changes or cost_changes:
                logger.info("Band/tier changes detected and applied automatically")
                
                # Clear cached models data to force reload with new assignments
                DynamicModelSelector._cached_models_data = None
                self._load_cached_data()
            else:
                logger.debug("No band/tier configuration changes detected")
                
        except Exception as e:
            logger.error(f"Failed to auto-detect band changes: {e}")
    
    def select_models_by_context_band(self, band: str, max_count: int = 5) -> List[Dict]:
        """Select models based on context window band"""
        matching_models = []
        
        for model in self.models_data:
            # Use context_window if context_numeric is not available
            context_tokens = model.get('context_numeric', model.get('context_window', 0))
            if self.get_context_window_band(context_tokens) == band:
                matching_models.append(model)
        
        # Sort by rank and return top N
        matching_models.sort(key=lambda x: x.get('rank', 999))
        return matching_models[:max_count]
    
    def select_models_by_cost_tier(self, tier: str, max_count: int = 5) -> List[Dict]:
        """Select models based on cost tier band"""
        matching_models = []
        
        for model in self.models_data:
            # Use input_cost if input_cost_numeric is not available
            input_cost = model.get('input_cost_numeric', model.get('input_cost', 0.0))
            if self.get_cost_tier_band(input_cost) == tier:
                matching_models.append(model)
        
        # Sort by rank and return top N
        matching_models.sort(key=lambda x: x.get('rank', 999))
        return matching_models[:max_count]
    
    def select_consensus_models(self, org_level: str) -> Tuple[List[str], float]:
        """
        Select models for consensus analysis based on IT organizational level with fallback recovery.
        
        Uses table-driven selection from available-models.md organizational data.
        Implements cascading fallback strategies when primary selection fails.
        
        Args:
            org_level: 'junior' (basic), 'senior' (review), or 'executive' (critical)
            
        Returns:
            Tuple of (model_names, estimated_cost)
        """
        try:
            # Primary selection: Get models directly assigned to this organizational level
            org_models = [m for m in self.models_data if m['org_level'] == org_level.lower()]
            
            if not org_models:
                logger.warning(f"No models found for org level: {org_level}")
                return self._select_with_fallback_recovery(org_level)
            
            # Sort by rank (best first) and select top models for consensus
            org_models = sorted(org_models, key=lambda x: x['rank'])
            
            # Select appropriate number based on org level
            if org_level.lower() == "junior":
                selected = org_models[:3]  # Junior: Keep it simple with 3 models max
            elif org_level.lower() == "senior":  
                selected = org_models[:5]  # Senior: Professional breadth with 5 models
            else:  # executive
                selected = org_models[:6]  # Executive: Comprehensive analysis with 6+ models
            
            # Validate minimum requirements with fallback
            min_required = {"junior": 2, "senior": 3, "executive": 4}  # Reduced minimums for reliability
            if len(selected) < min_required.get(org_level.lower(), 2):
                logger.warning(f"Insufficient primary models for {org_level}: {len(selected)} found, {min_required.get(org_level.lower())} required")
                return self._select_with_fallback_recovery(org_level)
            
            model_names = [m['name'] for m in selected]
            
            # Calculate estimated cost based on usage patterns
            total_cost = self._estimate_consensus_cost(selected, org_level)
            
            logger.info(f"Selected {len(selected)} {org_level} models: {model_names}")
            
            return model_names, total_cost
            
        except Exception as e:
            logger.error(f"Primary model selection failed for {org_level}: {e}")
            return self._select_with_fallback_recovery(org_level)
    
    def select_layered_consensus_models(self, org_level: str) -> Tuple[Dict[str, List[str]], float]:
        """
        Select models using layered organizational approach with fallback recovery.
        
        Builds on previous tiers instead of replacing them:
        - Junior: 3 free models for basic roles
        - Senior: 3 free models + 3 value models (6 total)
        - Executive: 3 free + 3 value + 2 premium models (8 total)
        
        Implements fallback strategies when organizational levels have insufficient models.
        
        Args:
            org_level: 'junior', 'senior', or 'executive'
            
        Returns:
            Tuple of (layered_models_dict, total_estimated_cost)
            where layered_models_dict = {"junior": [...], "senior": [...], "executive": [...]}
        """
        try:
            layered_models = {}
            total_cost = 0.0
            
            # Always include junior level (basic roles with free models)
            junior_models = [m for m in self.models_data if m['org_level'] == 'junior']
            junior_models = sorted(junior_models, key=lambda x: x['rank'])[:3]
            
            # Fallback for insufficient junior models
            if len(junior_models) < 2:
                logger.warning(f"Insufficient junior models: {len(junior_models)} found, need at least 2")
                junior_models = self._get_fallback_models_for_tier("junior", min_count=2, max_count=3)
            
            layered_models["junior"] = [m['name'] for m in junior_models]
            total_cost += self._estimate_consensus_cost(junior_models, "junior")
            
            if org_level.lower() in ["senior", "executive"]:
                # Add senior level (professional roles with value models)
                senior_models = [m for m in self.models_data if m['org_level'] == 'senior']
                senior_models = sorted(senior_models, key=lambda x: x['rank'])[:3]
                
                # Fallback for insufficient senior models
                if len(senior_models) < 2:
                    logger.warning(f"Insufficient senior models: {len(senior_models)} found, need at least 2")
                    senior_models = self._get_fallback_models_for_tier("senior", min_count=2, max_count=3)
                
                layered_models["senior"] = [m['name'] for m in senior_models] 
                total_cost += self._estimate_consensus_cost(senior_models, "senior")
            
            if org_level.lower() == "executive":
                # Add executive level (strategic roles with premium models)
                exec_models = [m for m in self.models_data if m['org_level'] == 'executive']
                exec_models = sorted(exec_models, key=lambda x: x['rank'])[:2]
                
                # Fallback for insufficient executive models
                if len(exec_models) < 1:
                    logger.warning(f"Insufficient executive models: {len(exec_models)} found, need at least 1")
                    exec_models = self._get_fallback_models_for_tier("executive", min_count=1, max_count=2)
                
                layered_models["executive"] = [m['name'] for m in exec_models]
                total_cost += self._estimate_consensus_cost(exec_models, "executive")
            
            # Create flat model list for compatibility and validate minimum requirements
            all_models = []
            for level_models in layered_models.values():
                all_models.extend(level_models)
            
            # Reduced minimum requirements for better reliability
            min_required = {"junior": 2, "senior": 4, "executive": 6}
            if len(all_models) < min_required.get(org_level.lower(), 2):
                logger.warning(f"Layered selection insufficient: {len(all_models)} models, {min_required.get(org_level.lower())} required")
                return self._select_layered_with_emergency_fallback(org_level)
            
            logger.info(f"Layered {org_level} selection: {len(all_models)} total models")
            logger.info(f"Breakdown: {[(k, len(v)) for k, v in layered_models.items()]}")
            
            return layered_models, total_cost
            
        except Exception as e:
            logger.error(f"Layered consensus selection failed for {org_level}: {e}")
            return self._select_layered_with_emergency_fallback(org_level)
    
    def create_layered_role_assignments(self, layered_models: Dict[str, List[str]]) -> List[Dict]:
        """
        Create role assignments for layered consensus models.
        
        Maps organizational levels to appropriate roles:
        - Junior: Basic roles (Code Reviewer, Security Checker, Technical Validator)
        - Senior: Professional roles (Security Engineer, Senior Developer, System Architect)  
        - Executive: Strategic roles (Lead Architect, Technical Director)
        
        Args:
            layered_models: Dict from select_layered_consensus_models()
            
        Returns:
            List of {"model": model_name, "stance": stance} assignments
        """
        assignments = []
        
        # Junior level roles (basic analysis)
        junior_roles = [
            {"stance": "for"},      # Code Reviewer
            {"stance": "against"},  # Security Checker
            {"stance": "neutral"}   # Technical Validator
        ]
        
        if "junior" in layered_models:
            for i, model in enumerate(layered_models["junior"]):
                role = junior_roles[i % len(junior_roles)]
                assignments.append({
                    "model": model,
                    "stance": role["stance"]
                })
        
        # Senior level roles (professional analysis)
        senior_roles = [
            {"stance": "against"},  # Security Engineer
            {"stance": "for"},      # Senior Developer
            {"stance": "neutral"}   # System Architect
        ]
        
        if "senior" in layered_models:
            for i, model in enumerate(layered_models["senior"]):
                role = senior_roles[i % len(senior_roles)]
                assignments.append({
                    "model": model,
                    "stance": role["stance"]
                })
        
        # Executive level roles (strategic analysis)
        executive_roles = [
            {"stance": "neutral"},  # Lead Architect
            {"stance": "for"}       # Technical Director
        ]
        
        if "executive" in layered_models:
            for i, model in enumerate(layered_models["executive"]):
                role = executive_roles[i % len(executive_roles)]
                assignments.append({
                    "model": model,
                    "stance": role["stance"]
                })
        
        return assignments
    
    def _get_fallback_models_for_tier(self, target_tier: str, min_count: int, max_count: int) -> List[Dict]:
        """
        Get fallback models for a specific tier when primary selection fails.
        
        Args:
            target_tier: The organizational tier needing models
            min_count: Minimum models required
            max_count: Maximum models to select
            
        Returns:
            List of model dictionaries for fallback use
        """
        logger.info(f"Getting fallback models for {target_tier} tier (need {min_count}-{max_count})")
        
        # Try to find models from other tiers as fallbacks
        tier_priority = {"executive": 3, "senior": 2, "junior": 1}
        target_priority = tier_priority.get(target_tier, 1)
        
        # Get all available models, prioritize similar tiers
        all_available = []
        for tier in ["junior", "senior", "executive"]:
            tier_models = [m for m in self.models_data if m['org_level'] == tier]
            for model in tier_models:
                model_priority = abs(tier_priority.get(tier, 1) - target_priority)
                all_available.append((model_priority, model['rank'], model))
        
        # Sort by tier similarity first, then by rank
        all_available.sort(key=lambda x: (x[0], x[1]))
        
        # Select the best available models up to max_count
        fallback_models = [item[2] for item in all_available[:max_count]]
        
        if len(fallback_models) >= min_count:
            logger.info(f"Fallback success: Found {len(fallback_models)} models for {target_tier}")
            return fallback_models
        else:
            logger.warning(f"Fallback insufficient: Only {len(fallback_models)} models available for {target_tier}")
            return fallback_models  # Return what we have, even if insufficient
    
    def _select_layered_with_emergency_fallback(self, org_level: str) -> Tuple[Dict[str, List[str]], float]:
        """
        Emergency fallback for layered consensus when all tier-based approaches fail.
        
        Args:
            org_level: Target organizational level
            
        Returns:
            Tuple of emergency layered models and estimated cost
        """
        logger.warning(f"Emergency layered fallback for {org_level}")
        
        try:
            # Get all available models regardless of tier
            all_models = sorted(self.models_data, key=lambda x: x['rank'])
            
            if not all_models:
                raise RuntimeError("No models available for emergency fallback")
            
            # Create emergency layered structure
            emergency_layered = {"junior": [], "senior": [], "executive": []}
            total_cost = 0.0
            
            # Distribute models across tiers based on what's available
            models_per_tier = min(3, len(all_models) // 3 + 1) if len(all_models) >= 3 else 1
            
            # Assign models to tiers
            for i, model in enumerate(all_models[:9]):  # Limit to 9 models max
                tier_index = i % 3
                tier_name = ["junior", "senior", "executive"][tier_index]
                emergency_layered[tier_name].append(model['name'])
                total_cost += self._estimate_consensus_cost([model], tier_name)
            
            # Remove empty tiers
            emergency_layered = {k: v for k, v in emergency_layered.items() if v}
            
            # Ensure we meet minimum requirements
            total_models = sum(len(models) for models in emergency_layered.values())
            if total_models >= 2:
                logger.warning(f"Emergency fallback SUCCESS: {total_models} models distributed across tiers")
                return emergency_layered, total_cost
            else:
                raise RuntimeError(f"Emergency fallback failed: Only {total_models} models available")
                
        except Exception as e:
            logger.error(f"Emergency layered fallback failed: {e}")
            # Return minimal viable structure
            if self.models_data:
                minimal_model = self.models_data[0]
                minimal_layered = {"junior": [minimal_model['name']]}
                minimal_cost = self._estimate_consensus_cost([minimal_model], "junior")
                logger.error(f"Returning minimal viable consensus: 1 model")
                return minimal_layered, minimal_cost
            else:
                raise RuntimeError("Complete failure: No models available at all")
    
    def _estimate_consensus_cost(self, models: List[Dict], org_level: str) -> float:
        """Estimate cost for consensus analysis based on usage patterns"""
        
        # Usage multipliers based on organizational level
        usage_factors = {
            "junior": 0.001,    # Minimal usage for basic analysis
            "senior": 0.003,    # Standard professional usage
            "executive": 0.005  # Comprehensive executive analysis
        }
        
        factor = usage_factors.get(org_level.lower(), 0.001)
        total_cost = sum(m['output_cost'] * factor for m in models)
        
        return total_cost
    
    def _select_by_price_tier(self, org_level: str) -> Tuple[List[str], float]:
        """Fallback selection using old price tier logic"""
        selected_models = []
        total_cost = 0.0
        
        if org_level == "junior":
            free_models = self.get_models_by_tier("free")[:3]
            selected_models.extend([m['name'] for m in free_models])
            
            if len(selected_models) < 2:
                economy_models = self.get_models_by_tier("economy")[:2]
                selected_models.extend([m['name'] for m in economy_models])
                total_cost += sum(m['output_cost'] * 0.001 for m in economy_models)
        
        elif org_level == "senior":
            economy_models = self.get_models_by_tier("economy")[:2]
            value_models = self.get_models_by_tier("value")[:3]
            
            selected_models.extend([m['name'] for m in economy_models])
            selected_models.extend([m['name'] for m in value_models])
            
            total_cost = (
                sum(m['output_cost'] * 0.002 for m in economy_models) +
                sum(m['output_cost'] * 0.003 for m in value_models)
            )
        
        elif org_level == "executive":
            value_models = self.get_models_by_tier("value")[:2]
            premium_models = self.get_models_by_tier("premium")[:4]
            
            selected_models.extend([m['name'] for m in value_models])
            selected_models.extend([m['name'] for m in premium_models])
            
            total_cost = (
                sum(m['output_cost'] * 0.003 for m in value_models) +
                sum(m['output_cost'] * 0.005 for m in premium_models)
            )
        
        return selected_models, total_cost
    
    def _select_with_fallback_recovery(self, org_level: str) -> Tuple[List[str], float]:
        """
        Implement cascading fallback strategies when primary model selection fails.
        
        Fallback Strategy:
        1. Cross-tier selection (use available models from other org levels)
        2. Price-tier based selection (legacy approach)
        3. Emergency selection (any available models)
        4. Minimal viable consensus (at least 2 models)
        
        Args:
            org_level: Target organizational level
            
        Returns:
            Tuple of (model_names, estimated_cost) with fallback models
        """
        logger.info(f"Initiating fallback recovery for {org_level} level")
        
        try:
            # Fallback 1: Cross-tier selection - use models from any organizational level
            logger.info("Attempting Fallback 1: Cross-tier selection")
            
            all_org_models = []
            for level in ["junior", "senior", "executive"]:
                level_models = [m for m in self.models_data if m['org_level'] == level]
                all_org_models.extend(level_models)
            
            if all_org_models:
                # Sort by rank and prefer models from similar or higher tiers
                tier_priority = {"executive": 3, "senior": 2, "junior": 1}
                target_priority = tier_priority.get(org_level.lower(), 1)
                
                # Sort by tier preference then rank
                all_org_models.sort(key=lambda x: (
                    abs(tier_priority.get(x['org_level'], 1) - target_priority),  # Prefer similar tiers
                    x['rank']  # Then by quality rank
                ))
                
                # Select appropriate count for consensus
                min_count = {"junior": 2, "senior": 3, "executive": 4}
                max_count = {"junior": 4, "senior": 6, "executive": 8}
                
                target_count = min_count.get(org_level.lower(), 2)
                max_available = max_count.get(org_level.lower(), 4)
                
                selected = all_org_models[:min(max_available, len(all_org_models))]
                
                if len(selected) >= target_count:
                    model_names = [m['name'] for m in selected]
                    total_cost = self._estimate_consensus_cost(selected, org_level)
                    logger.info(f"Fallback 1 SUCCESS: Selected {len(selected)} cross-tier models for {org_level}")
                    return model_names, total_cost
        
            # Fallback 2: Price-tier based selection (legacy approach)
            logger.info("Attempting Fallback 2: Price-tier selection")
            try:
                fallback_models, fallback_cost = self._select_by_price_tier(org_level)
                if fallback_models and len(fallback_models) >= 2:
                    logger.info(f"Fallback 2 SUCCESS: Selected {len(fallback_models)} price-tier models")
                    return fallback_models, fallback_cost
            except Exception as e:
                logger.warning(f"Fallback 2 failed: {e}")
            
            # Fallback 3: Emergency selection - any available models
            logger.info("Attempting Fallback 3: Emergency selection")
            if self.models_data and len(self.models_data) >= 2:
                # Sort by rank and take best available
                emergency_models = sorted(self.models_data, key=lambda x: x['rank'])[:4]
                model_names = [m['name'] for m in emergency_models]
                total_cost = self._estimate_consensus_cost(emergency_models, org_level)
                logger.info(f"Fallback 3 SUCCESS: Emergency selection of {len(emergency_models)} models")
                return model_names, total_cost
            
            # Fallback 4: Minimal viable consensus - absolute minimum
            logger.warning("Attempting Fallback 4: Minimal viable consensus")
            if self.models_data and len(self.models_data) >= 1:
                # Use whatever models are available, even if below recommended minimum
                minimal_models = sorted(self.models_data, key=lambda x: x['rank'])[:2]
                model_names = [m['name'] for m in minimal_models]
                total_cost = self._estimate_consensus_cost(minimal_models, org_level)
                logger.warning(f"Fallback 4 SUCCESS: Minimal selection of {len(minimal_models)} models")
                return model_names, total_cost
            
            # Ultimate fallback: No models available at all
            logger.error(f"FALLBACK COMPLETE FAILURE: No models available for {org_level}")
            raise RuntimeError(f"Complete fallback failure: No models available for {org_level} consensus")
            
        except Exception as e:
            logger.error(f"Fallback recovery failed for {org_level}: {e}")
            raise RuntimeError(f"Fallback recovery failed: {str(e)}")
    
    def get_best_model_for_org_role(self, role: str, org_level: str) -> Optional[str]:
        """Get the best model for a specific organizational role and level using table data"""
        
        # Query models directly from table using role and org_level columns
        matching_models = [
            m for m in self.models_data 
            if m['role'] == role.lower() and m['org_level'] == org_level.lower()
        ]
        
        if matching_models:
            # Return the best ranked model for this exact role/level combination
            best_model = min(matching_models, key=lambda x: x['rank'])
            return best_model['name']
        
        # Fallback 1: Same org level, any role
        org_level_models = [
            m for m in self.models_data 
            if m['org_level'] == org_level.lower()
        ]
        
        if org_level_models:
            best_model = min(org_level_models, key=lambda x: x['rank'])
            logger.info(f"Fallback: Using {best_model['name']} (role: {best_model['role']}) for requested {role}")
            return best_model['name']
        
        # Fallback 2: Same role, any org level (prefer higher levels)
        role_models = [
            m for m in self.models_data 
            if m['role'] == role.lower()
        ]
        
        if role_models:
            # Sort by org level priority: executive > senior > junior
            org_priority = {"executive": 3, "senior": 2, "junior": 1}
            best_model = max(role_models, key=lambda x: (org_priority.get(x['org_level'], 0), -x['rank']))
            logger.info(f"Fallback: Using {best_model['name']} ({best_model['org_level']}) for {org_level} level request")
            return best_model['name']
        
        # Final fallback: Best model for org level
        if org_level.lower() == "executive":
            executive_models = [m for m in self.models_data if m['org_level'] == 'executive']
            if executive_models:
                return min(executive_models, key=lambda x: x['rank'])['name']
        elif org_level.lower() == "senior":
            senior_models = [m for m in self.models_data if m['org_level'] == 'senior']
            if senior_models:
                return min(senior_models, key=lambda x: x['rank'])['name']
        else:  # junior
            junior_models = [m for m in self.models_data if m['org_level'] == 'junior']
            if junior_models:
                return min(junior_models, key=lambda x: x['rank'])['name']
        
        logger.warning(f"No suitable model found for role: {role}, org_level: {org_level}")
        return None
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get detailed info for a specific model"""
        return self.parsed_models.get(model_name)
    
    def get_large_context_models(self, min_context: int = 500000) -> List[str]:
        """Get models with large context windows (for big datasets)"""
        large_context = [m for m in self.models_data if m['context_window'] >= min_context]
        return [m['name'] for m in sorted(large_context, key=lambda x: x['context_window'], reverse=True)]
    
    # ===== NEW CENTRALIZED BAND METHODS =====
    
    def get_role_assignment_band(self, model_data: Dict) -> str:
        """
        Determine the appropriate role assignment band for a model based on centralized criteria.
        
        Args:
            model_data: Dictionary containing model information
            
        Returns:
            Band name for role assignment
        """
        if not self.bands_config:
            return "validation_roles"  # default fallback
            
        role_bands = self.bands_config.get("role_assignment_bands", {})
        
        for band_name, band_config in role_bands.items():
            # Skip metadata fields
            if not isinstance(band_config, dict) or 'criteria' not in band_config:
                continue
                
            criteria = band_config['criteria']
            matches = True
            
            # Check specialization criteria
            if 'specialization' in criteria:
                model_spec = model_data.get('specialization', '')
                if model_spec not in criteria['specialization']:
                    matches = False
                    continue
            
            # Check performance criteria
            if 'min_humaneval' in criteria:
                model_score = model_data.get('humaneval_score', 0)
                if model_score < criteria['min_humaneval']:
                    matches = False
                    continue
            
            # Check cost criteria
            if 'max_cost' in criteria:
                model_cost = max(model_data.get('input_cost', 0), model_data.get('output_cost', 0))
                if model_cost > criteria['max_cost']:
                    matches = False
                    continue
            
            # Check tier criteria
            if 'tier' in criteria:
                model_tier = model_data.get('tier', '')
                if model_tier not in criteria['tier']:
                    matches = False
                    continue
            
            # Check context criteria
            if 'min_context' in criteria:
                model_context = model_data.get('context_window', 0)
                if model_context < criteria['min_context']:
                    matches = False
                    continue
            
            # Check cost tier criteria
            if 'cost_tier' in criteria:
                model_cost_tier = self.get_cost_tier_band(
                    model_data.get('input_cost', 0), 
                    model_data.get('output_cost', 0)
                )
                if model_cost_tier not in criteria['cost_tier']:
                    matches = False
                    continue
            
            if matches:
                return band_name
        
        return "validation_roles"  # default fallback
    
    def get_rank_assignment_band(self, model_data: Dict) -> str:
        """
        Determine the appropriate rank assignment band for a model based on centralized criteria.
        
        Args:
            model_data: Dictionary containing model information
            
        Returns:
            Band name for rank assignment
        """
        if not self.bands_config:
            return "tier3_efficient"  # default fallback
            
        rank_bands = self.bands_config.get("rank_assignment_bands", {})
        
        for band_name, band_config in rank_bands.items():
            # Skip metadata fields
            if not isinstance(band_config, dict) or 'criteria' not in band_config:
                continue
                
            criteria = band_config['criteria']
            matches = True
            
            # Check performance criteria
            if 'min_humaneval' in criteria:
                model_score = model_data.get('humaneval_score', 0)
                if model_score < criteria['min_humaneval']:
                    matches = False
                    continue
            
            # Check tier criteria
            if 'tier' in criteria:
                model_tier = model_data.get('tier', '')
                if model_tier not in criteria['tier']:
                    matches = False
                    continue
            
            # Check context criteria
            if 'min_context' in criteria:
                model_context = model_data.get('context_window', 0)
                if model_context < criteria['min_context']:
                    matches = False
                    continue
            
            # Check provider criteria
            if 'provider' in criteria:
                model_provider = model_data.get('provider', '')
                if model_provider not in criteria['provider']:
                    matches = False
                    continue
            
            # Check cost criteria
            if 'max_cost' in criteria:
                model_cost = max(model_data.get('input_cost', 0), model_data.get('output_cost', 0))
                if model_cost > criteria['max_cost']:
                    matches = False
                    continue
            
            # Check cost tier criteria
            if 'cost_tier' in criteria:
                model_cost_tier = self.get_cost_tier_band(
                    model_data.get('input_cost', 0), 
                    model_data.get('output_cost', 0)
                )
                if model_cost_tier not in criteria['cost_tier']:
                    matches = False
                    continue
            
            # Check specialization criteria
            if 'specialization' in criteria:
                model_spec = model_data.get('specialization', '')
                if model_spec not in criteria['specialization']:
                    matches = False
                    continue
            
            if matches:
                return band_name
        
        return "tier3_efficient"  # default fallback
    
    def get_strength_classification_band(self, model_data: Dict) -> str:
        """
        Determine the appropriate strength classification band for a model based on centralized criteria.
        
        Args:
            model_data: Dictionary containing model information
            
        Returns:
            Band name for strength classification
        """
        if not self.bands_config:
            return "balanced"  # default fallback
            
        strength_bands = self.bands_config.get("strength_classification_bands", {})
        
        for band_name, band_config in strength_bands.items():
            # Skip metadata fields
            if not isinstance(band_config, dict) or 'criteria' not in band_config:
                continue
                
            criteria = band_config['criteria']
            matches = True
            
            # Check performance criteria
            if 'min_humaneval' in criteria:
                model_score = model_data.get('humaneval_score', 0)
                if model_score < criteria['min_humaneval']:
                    matches = False
                    continue
            
            # Check provider criteria
            if 'provider' in criteria:
                model_provider = model_data.get('provider', '')
                if model_provider not in criteria['provider']:
                    matches = False
                    continue
            
            # Check tier criteria
            if 'tier' in criteria:
                model_tier = model_data.get('tier', '')
                if model_tier not in criteria['tier']:
                    matches = False
                    continue
            
            # Check cost criteria
            if 'max_output_cost' in criteria:
                model_cost = model_data.get('output_cost', 0)
                if model_cost > criteria['max_output_cost']:
                    matches = False
                    continue
            
            # Check cost tier criteria
            if 'cost_tier' in criteria:
                model_cost_tier = self.get_cost_tier_band(
                    model_data.get('input_cost', 0), 
                    model_data.get('output_cost', 0)
                )
                if model_cost_tier not in criteria['cost_tier']:
                    matches = False
                    continue
            
            # Check context criteria
            if 'min_context' in criteria:
                model_context = model_data.get('context_window', 0)
                if model_context < criteria['min_context']:
                    matches = False
                    continue
            
            # Check specialization criteria
            if 'specialization' in criteria:
                model_spec = model_data.get('specialization', '')
                if model_spec not in criteria['specialization']:
                    matches = False
                    continue
            
            # Special criteria: cost_efficiency_score
            if 'cost_efficiency_score' in criteria:
                # Calculate cost efficiency (performance per dollar)
                input_cost = model_data.get('input_cost', 0)
                output_cost = model_data.get('output_cost', 0)
                avg_cost = (input_cost + output_cost) / 2 if (input_cost + output_cost) > 0 else 1
                humaneval = model_data.get('humaneval_score', 0)
                efficiency = humaneval / avg_cost if avg_cost > 0 else 0
                
                # For now, use a simple threshold (can be enhanced with percentile calculation)
                if criteria['cost_efficiency_score'] == "top_tercile" and efficiency < 10.0:
                    matches = False
                    continue
            
            if matches:
                return band_name
        
        return "balanced"  # default fallback
    
    def reassign_models_to_role_bands(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Reassign all models to role assignment bands based on current band configuration.
        
        Returns:
            Dict mapping band names to role assignments and model lists
        """
        if not self.bands_config:
            return {}
            
        role_bands = self.bands_config.get("role_assignment_bands", {})
        band_assignments = {}
        
        # Initialize band assignments
        for band_name, band_config in role_bands.items():
            if isinstance(band_config, dict) and 'roles' in band_config:
                band_assignments[band_name] = {
                    'roles': band_config['roles'],
                    'models': []
                }
        
        logger.info("Reassigning models to role assignment bands based on current configuration")
        
        for model in self.models_data:
            band = self.get_role_assignment_band(model)
            
            if band in band_assignments:
                band_assignments[band]['models'].append(model['name'])
                logger.debug(f"Assigned {model['name']} to {band} role band")
        
        # Log the reassignment summary
        for band_name, assignment in band_assignments.items():
            models = assignment['models']
            roles = assignment['roles']
            logger.info(f"{band_name} band: {len(models)} models, roles: {roles}")
        
        return band_assignments
    
    def reassign_models_to_rank_bands(self) -> Dict[str, List[str]]:
        """
        Reassign all models to rank assignment bands based on current band configuration.
        
        Returns:
            Dict mapping band names to lists of model names in each band
        """
        if not self.bands_config:
            return {}
            
        rank_bands = self.bands_config.get("rank_assignment_bands", {})
        band_assignments = {}
        
        # Initialize band assignments
        for band_name, band_config in rank_bands.items():
            if isinstance(band_config, dict) and 'rank_range' in band_config:
                band_assignments[band_name] = []
        
        logger.info("Reassigning models to rank assignment bands based on current configuration")
        
        for model in self.models_data:
            band = self.get_rank_assignment_band(model)
            
            if band in band_assignments:
                band_assignments[band].append(model['name'])
                logger.debug(f"Assigned {model['name']} to {band} rank band")
        
        # Log the reassignment summary
        for band_name, models in band_assignments.items():
            logger.info(f"{band_name} band: {len(models)} models - {models}")
        
        return band_assignments
    
    def reassign_models_to_strength_bands(self) -> Dict[str, List[str]]:
        """
        Reassign all models to strength classification bands based on current band configuration.
        
        Returns:
            Dict mapping band names to lists of model names in each band
        """
        if not self.bands_config:
            return {}
            
        strength_bands = self.bands_config.get("strength_classification_bands", {})
        band_assignments = {}
        
        # Initialize band assignments
        for band_name, band_config in strength_bands.items():
            if isinstance(band_config, dict) and 'description' in band_config:
                band_assignments[band_name] = []
        
        logger.info("Reassigning models to strength classification bands based on current configuration")
        
        for model in self.models_data:
            band = self.get_strength_classification_band(model)
            
            if band in band_assignments:
                band_assignments[band].append(model['name'])
                logger.debug(f"Assigned {model['name']} to {band} strength band")
        
        # Log the reassignment summary
        for band_name, models in band_assignments.items():
            logger.info(f"{band_name} band: {len(models)} models - {models}")
        
        return band_assignments


# Global instance for efficient reuse
_model_selector = None

def get_model_selector() -> DynamicModelSelector:
    """Get the global model selector instance"""
    global _model_selector
    if _model_selector is None:
        _model_selector = DynamicModelSelector()
    return _model_selector