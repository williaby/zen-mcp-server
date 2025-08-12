# Centralized Band Configuration: Single Source of Truth

## Overview
The context window and cost tier bands now use a centralized configuration approach where you update ranges in one place (`bands_config.json`) and all model assignments automatically cascade to reflect the new structure.

## Example Scenario: Updating Context Window Bands

### Current Configuration (bands_config.json):
```json
{
  "context_window_bands": {
    "compact": {"max_tokens": 65000},
    "standard": {"min_tokens": 65001, "max_tokens": 200000},
    "extended": {"min_tokens": 200001, "max_tokens": 999999}, 
    "large": {"min_tokens": 1000000}
  }
}
```

### Current Model Distribution:
```
Compact (≤65K): 7 models
├── llama-3.2 (32K), phi-4 (32K), deepseek-r1 (65K), etc.

Standard (65K-200K): 9 models  
├── claude-sonnet-4 (200K), gpt-5-mini (200K), o4-mini (200K), etc.

Extended (200K-999K): 6 models
├── gpt-5 (400K), claude-opus-4.1 (200K), gemini-2.5-pro (1M), etc.

Large (1M+): 3 models
├── gemini-2.5-flash (1M), gemini-2.5-pro (1M), qwen2.5-vl (1M)
```

## Change Request: Large Models = 1M+ Only

### Step 1: Update bands_config.json (Single Change)
```json
{
  "context_window_bands": {
    "compact": {"max_tokens": 65000},
    "standard": {"min_tokens": 65001, "max_tokens": 200000},  
    "extended": {"min_tokens": 200001, "max_tokens": 999999},
    "large": {"min_tokens": 1000000}  // ← Only this changed
  }
}
```

### Step 2: Automatic Model Reassignment

When the DynamicModelSelector initializes, it detects the band change and automatically:

1. **Recalculates all model assignments** based on new ranges
2. **Updates models.csv** with new `context_band` column
3. **Creates assignment cache** to track future changes
4. **Logs the reassignment process**

### Result: Automatic Model Migration

```
Compact (≤65K): 7 models [UNCHANGED]
├── llama-3.2 (32K), phi-4 (32K), deepseek-r1 (65K), etc.

Standard (65K-200K): 9 models [UNCHANGED]
├── claude-sonnet-4 (200K), gpt-5-mini (200K), o4-mini (200K), etc.

Extended (200K-999K): 8 models [+2 MOVED FROM LARGE]
├── gpt-5 (400K), claude-opus-4.1 (200K) ← MOVED from Large
├── Plus existing extended models

Large (1M+): 1 model [ONLY TRUE 1M+ MODELS]
├── gemini-2.5-flash (1M), gemini-2.5-pro (1M) ← ONLY these qualify
```

### Log Output Example:
```
2025-08-11 10:30:15 INFO: Context window band changes detected - reassigning models
2025-08-11 10:30:15 INFO: Assigned gpt-5 (400,000 tokens) to extended band
2025-08-11 10:30:15 INFO: Assigned claude-opus-4.1 (200,000 tokens) to extended band  
2025-08-11 10:30:15 INFO: Extended band: 8 models - [gpt-5, claude-opus-4.1, ...]
2025-08-11 10:30:15 INFO: Large band: 1 models - [gemini-2.5-pro]
2025-08-11 10:30:15 INFO: Updated models.csv with new context window band assignments
```

## Cost Tier Example: Moving Economy Threshold

### Current Cost Tiers:
```json
{
  "cost_tier_bands": {
    "free": {"max_cost": 0.0},
    "economy": {"min_cost": 0.01, "max_cost": 1.0},
    "value": {"min_cost": 1.01, "max_cost": 10.0},
    "premium": {"min_cost": 10.01}
  }
}
```

### Change: Economy becomes ≤$2.00
```json
{
  "cost_tier_bands": {
    "free": {"max_cost": 0.0},
    "economy": {"min_cost": 0.01, "max_cost": 2.0},  // ← Changed from 1.0
    "value": {"min_cost": 2.01, "max_cost": 10.0},   // ← Auto-adjusted
    "premium": {"min_cost": 10.01}
  }
}
```

### Automatic Result:
Models costing $1.01-$2.00 automatically move from **Value** → **Economy** tier:
- `gpt-5-nano` ($0.40) stays in Economy
- `mistral-large` ($2.00) moves from Value → Economy  
- `claude-sonnet-4` ($3.00) stays in Value

## Implementation Benefits

### ✅ Single Source of Truth
- **One file controls all assignments**: `bands_config.json`
- **No manual model updates needed**: Automatic reassignment
- **Consistent across all tools**: All model selection uses same bands

### 🔄 Automatic Cascading  
- **Change detection**: Compares current vs cached assignments
- **Atomic updates**: CSV file updated safely with temp files
- **Cache management**: Tracks changes to avoid unnecessary updates
- **Error handling**: Rollback on failure, logging for transparency

### 🚀 Zero Downtime Updates
- **Hot configuration reload**: Changes apply on next selector initialization  
- **Backwards compatibility**: Graceful fallback if bands missing
- **Validation**: Ensures models always assigned to valid bands

### 📊 Transparency & Control
- **Detailed logging**: See exactly which models moved where
- **Assignment tracking**: Cache files show before/after state
- **Manual override**: Can still manually assign if needed
- **Audit trail**: All changes logged with timestamps

## Usage Pattern

```python
# 1. Update bands_config.json ranges
# 2. Restart any process using DynamicModelSelector
# 3. Check logs to see automatic reassignments
# 4. Verify models.csv for new assignments

# Or programmatically:
selector = DynamicModelSelector()  # Auto-detects changes on init
band_changes = selector.detect_and_apply_band_changes()
cost_changes = selector.detect_and_apply_cost_tier_changes()

if band_changes or cost_changes:
    print("Models automatically reassigned to new bands!")
```

This approach ensures that updating context window or cost tier definitions is a **single configuration change** that automatically cascades throughout the entire model management system without requiring manual updates to individual model records.