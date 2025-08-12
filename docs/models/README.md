# AI Models Infrastructure

This directory contains the complete AI model selection and evaluation infrastructure for the Zen MCP Server.

## Overview

The dynamic model selector provides intelligent model routing across multiple LLM platforms, enabling requests by model type rather than specific model names (e.g., "best free coding model", "executive-level reasoning model").

## File Structure

### Core Data Files

- **`models.csv`** - Master model database with 24+ models
- **`bands_config.json`** - Quantitative scoring bands and organizational requirements
- **`models_schema.json`** - JSON validation schema for model data structure

### Generated Views (Auto-updated)

- **`models_by_cost.csv`** - Models sorted by cost effectiveness (input + output cost)
- **`models_by_context.csv`** - Models sorted by context window size
- **`free_models.csv`** - Free tier models only (11+ models)
- **`coding_specialists.csv`** - Coding-focused models

## Centralized Band System Architecture

The model selection system uses a **centralized band configuration approach** where all model categorizations are controlled from a single source of truth (`bands_config.json`). This enables automatic model reassignment when criteria change.

### 🎯 **9 Centralized Band Categories**

#### 1. **Context Window Bands** (`context_window_bands`)
Automatically categorize models by context capacity:
- **Compact**: ≤65K tokens (6-8 models)
- **Standard**: 65K-200K tokens (8-10 models) 
- **Extended**: 200K-999K tokens (5-7 models)
- **Large**: 1M+ tokens (3-4 models)

#### 2. **Cost Tier Bands** (`cost_tier_bands`)
Automatically categorize models by pricing:
- **Free**: $0.00 (8 models, 32%)
- **Economy**: $0.01-$1.00 per million tokens (4-5 models)
- **Value**: $1.01-$10.00 per million tokens (6 models, 24%)
- **Premium**: $10.01+ per million tokens (6 models, 24%)

#### 3. **Performance Bands** (`performance_bands`)
Automatically categorize models by HumanEval scores:
- **Basic**: ≤65.0 (3-4 models)
- **Good**: 65.1-75.0 (6-8 models)
- **Excellent**: 75.1-85.0 (8-10 models)
- **Exceptional**: 85.1+ (4-6 models)

#### 4. **Tier Classification Bands** (`tier_classification_bands`)
Automatically assign strategic tiers based on combined criteria:
- **Free Champion**: Free + ≥60 HumanEval (8 models)
- **Value Tier**: ≤$2 cost + ≥70 HumanEval (6 models)
- **High Performance**: ≤$10 cost + ≥75 HumanEval (6 models)
- **Premium**: ≥$3 cost + ≥80 HumanEval (5 models)

#### 5. **Org Level Assignment Bands** (`org_level_assignment_bands`)
Automatically assign models to organizational levels:
- **Junior**: ≤$1 cost + ≥60 HumanEval + ≥32K context (8 models)
- **Senior**: ≤$10 cost + ≥70 HumanEval + ≥65K context (10 models)
- **Executive**: Unlimited cost + ≥80 HumanEval + ≥128K context (7 models)

#### 6. **Provider Trust Bands** (`provider_trust_bands`)
Automatically classify providers by trust score:
- **Tier 1 Trusted**: Score 9+ (OpenAI, Anthropic, Google)
- **Tier 2 Verified**: Score 8+ (Microsoft, Meta, Mistral)
- **Tier 3 Emerging**: Score 7+ (DeepSeek, Qwen, Perplexity)
- **Tier 4 Experimental**: Score 5+ (HuggingFace, others)

#### 7. **Role Assignment Bands** (`role_assignment_bands`)
Automatically assign professional roles based on specialization and performance:
- **Technical Roles**: Coding/debugging specialists → senior_developer, code_reviewer, qa_engineer
- **Architecture Roles**: Premium models ≥80 HumanEval → lead_architect, system_architect, technical_director
- **Analysis Roles**: Reasoning/security specialists → security_analyst, risk_analyst, research_lead
- **Validation Roles**: Free/economy models → technical_validator, security_checker

#### 8. **Rank Assignment Bands** (`rank_assignment_bands`)
Automatically assign model rankings based on quantitative criteria:
- **Tier 1 Flagship** (Ranks 1-5): Premium models from major providers ≥85 HumanEval
- **Tier 2 Professional** (Ranks 6-15): High-performance models ≥75 HumanEval
- **Tier 3 Efficient** (Ranks 16-25): Cost-effective models ≥65 HumanEval
- **Tier 4 Specialized** (Ranks 26-35): Experimental/specialized models ≥50 HumanEval

#### 9. **Strength Classification Bands** (`strength_classification_bands`)
Automatically assign strength descriptions based on performance characteristics:
- **Next Generation**: Flagship premium models ≥88 HumanEval from major providers
- **Advanced**: Professional-grade models ≥85 HumanEval with ≤$25 cost
- **Balanced**: Well-rounded models ≥75 HumanEval with good context
- **Efficient**: Cost-optimized models (top efficiency tercile)
- **Specialized**: Domain-specific models (vision, coding, debugging)
- **Experimental**: Emerging technology models

### 🔄 **Single Source of Truth Benefits**

#### Automatic Cascading Updates
```json
// Change context window definition in ONE place:
"large": {"min_tokens": 1000000}  // ← Only change needed

// Result: All models automatically reassign to new bands
// No manual CSV updates required
```

#### Dynamic Model Assignment
```python
# When bands_config.json changes:
selector = DynamicModelSelector()  # Auto-detects changes
band_changes = selector.detect_and_apply_band_changes()
# → Models automatically move to appropriate bands
# → CSV files automatically updated
# → Cache updated to track changes
```

#### Consistent Cross-Tool Usage
All model selection tools use the same band definitions:
- Context window selection: Uses `context_window_bands`
- Cost optimization: Uses `cost_tier_bands`  
- Role assignment: Uses `role_assignment_bands`
- Performance targeting: Uses `performance_bands`

### 📊 **Centralized Configuration Example**

When you update band definitions in `bands_config.json`, changes automatically cascade:

#### Before: Change Context Window Threshold
```json
{
  "context_window_bands": {
    "large": {"min_tokens": 500000}  // Old threshold
  }
}
```

#### After: Update Definition
```json  
{
  "context_window_bands": {
    "large": {"min_tokens": 1000000}  // New threshold - ONLY change needed
  }
}
```

#### Automatic Result:
- Models 500K-999K: Move from `large` → `extended` band
- Models 1M+: Remain in `large` band  
- CSV files automatically updated
- All tools immediately use new bands

### 🎯 **Configuration-Driven Architecture**

The entire model classification system is now **configuration-driven** rather than hard-coded:

| Category | Configuration File | Automatic Assignment |
|----------|-------------------|---------------------|
| **Context Windows** | `context_window_bands` | Based on token count |
| **Cost Tiers** | `cost_tier_bands` | Based on pricing |
| **Performance** | `performance_bands` | Based on HumanEval scores |
| **Roles** | `role_assignment_bands` | Based on specialization + performance |
| **Rankings** | `rank_assignment_bands` | Based on multi-criteria scoring |
| **Strengths** | `strength_classification_bands` | Based on combined characteristics |
| **Org Levels** | `org_level_assignment_bands` | Based on cost + performance + context |
| **Provider Trust** | `provider_trust_bands` | Based on trust scores |
| **Tier Classification** | `tier_classification_bands` | Based on cost + performance criteria |

## Model Categories

### Free Models (11 models)
High-quality models with $0 cost, perfect for development and cost-conscious production:

- **Free Champions**: Llama 405B:free, DeepSeek R1:free, Qwen Coder:free
- **Specialized Free**: Phi-4 (debugging), Qwen VL (vision), QwQ (reasoning)

### Coding Specialists
Models optimized for software development tasks:

- **Qwen3 Coder** - Leading coding-focused model
- **Qwen 2.5 Coder:free** - Free coding specialist
- **DeepSeek R1** - Advanced reasoning for complex coding problems

### Vision Models
Models with multimodal capabilities:

- **Qwen 2.5 VL:free** - Free vision-language model
- **Gemini 2.5 Pro** - Premium vision capabilities

## OpenRouter Integration

All models include direct OpenRouter URLs for:
- Real-time pricing verification
- Model documentation access
- API endpoint configuration
- Performance benchmarking data

### Free Model Logic

OpenRouter uses `:free` suffix to indicate free versions of paid models:
- `model-name` = Paid version
- `model-name:free` = Free version with usage limits

## Benchmark Scores

Models include performance metrics:

- **HumanEval Score**: Coding capability (0-100%)
- **SWE-bench Score**: Software engineering tasks (0-100%)

## Usage Examples

### Find Best Free Coding Model (Automatic Band Assignment)
```python
from tools.custom.dynamic_model_selector import DynamicModelSelector

selector = DynamicModelSelector()
model = selector.find_models(
    specialization="coding",
    org_level="junior",  # Automatically uses cost_tier_bands: free/economy
    max_results=1
)[0]
# Returns: qwen/qwen-2.5-coder-32b-instruct:free
# Role automatically assigned via role_assignment_bands: technical_roles
```

### Get Executive-Level Reasoning Model (Automatic Band Assignment)
```python
model = selector.find_models(
    specialization="reasoning", 
    org_level="executive",  # Automatically uses org_level_assignment_bands criteria
    max_results=1
)[0]
# Returns: openai/gpt-5 or anthropic/claude-opus-4.1
# Rank automatically assigned via rank_assignment_bands: tier1_flagship
# Strength automatically assigned via strength_classification_bands: next_generation
```

### Centralized Band Usage
```python
# All these selections use centralized band definitions:

# Context window selection (uses context_window_bands)
large_models = selector.get_large_context_models()

# Cost optimization (uses cost_tier_bands) 
economy_models = selector.find_models(cost_tier="economy")

# Performance targeting (uses performance_bands)
excellent_models = selector.find_models(performance_band="excellent")

# Role-based selection (uses role_assignment_bands)
architect_models = selector.find_models(role="lead_architect")
```

### Dynamic Band Reassignment
```python
# Detect and apply band changes automatically
selector = DynamicModelSelector()

# Check for context window band changes
context_changes = selector.detect_and_apply_band_changes()

# Check for cost tier band changes  
cost_changes = selector.detect_and_apply_cost_tier_changes()

# New: Check for role assignment changes
role_assignments = selector.reassign_models_to_role_bands()

# New: Check for rank assignment changes
rank_assignments = selector.reassign_models_to_rank_bands()

# New: Check for strength classification changes
strength_assignments = selector.reassign_models_to_strength_bands()

if any([context_changes, cost_changes]):
    print("Models automatically reassigned to new bands!")
```

## Data Validation

All model data is validated against `models_schema.json`:

- Required fields enforcement
- Type validation (integers, floats, enums)
- Value range validation (costs, context windows)
- URL format validation for OpenRouter links
- Date format validation for updates

## Automated Updates

The system supports automated model evaluation for new releases:

1. **Discovery**: Monitor OpenRouter for new models
2. **Evaluation**: Run benchmark tests on new models
3. **Classification**: Assign tier, org_level, and specialization
4. **Integration**: Update CSV and regenerate views

## Contributing

When adding new models:

1. Add entry to `models.csv` with all required fields
2. Validate against `models_schema.json`
3. Run model selector to regenerate view files
4. Update OpenRouter URLs to current model pages
5. Include benchmark scores when available

## Cost Management

The band system provides multiple cost optimization strategies:

- **Free-first**: Prioritize free models for development
- **Value-conscious**: Balance cost and performance 
- **Performance-first**: Select best models regardless of cost
- **Organizational**: Match model costs to user authority levels

This infrastructure enables sophisticated model selection while maintaining cost control and performance optimization across the entire development lifecycle.