# Dynamic Model Selector - Intelligent AI Model Routing

**Automatically select the best AI models based on organizational level, specialization, and performance requirements**

The `dynamic_model_selector` provides intelligent model routing across multiple LLM platforms, enabling requests by model type rather than specific model names (e.g., "best free coding model", "executive-level reasoning model").

## Thinking Mode

**Not applicable.** The dynamic model selector performs deterministic lookups and filtering based on pre-configured model data - no AI reasoning required for model selection logic.

## Model Recommendation

The dynamic model selector is the foundation tool that other components use to intelligently choose appropriate models. It maintains the centralized model database and selection algorithms.

## How It Works

The dynamic model selector uses a sophisticated multi-tier approach to model selection:

1. **Load centralized configuration**: Reads models.csv and bands_config.json for current model data
2. **Apply organizational filters**: Match requests to appropriate cost and performance tiers
3. **Filter by specialization**: Find models optimized for specific tasks (coding, reasoning, vision)
4. **Rank by performance**: Sort candidates by benchmark scores and quality metrics
5. **Return optimal selection**: Provide best-fit models with fallback strategies

## Example Usage

**Python API - Basic Selection:**
```python
from tools.custom.dynamic_model_selector import DynamicModelSelector

selector = DynamicModelSelector()
models, cost = selector.select_consensus_models("senior")
# Returns: (['anthropic/claude-sonnet-4', 'openai/gpt-5-mini', ...], 0.003)
```

**Organizational Level Selection:**
```python
# Get best model for specific role and level
model = selector.get_best_model_for_org_role("senior_developer", "senior")
# Returns: 'anthropic/claude-sonnet-4'

# Get layered consensus models
layered_models, cost = selector.select_layered_consensus_models("executive")
# Returns: ({'junior': [...], 'senior': [...], 'executive': [...]}, 0.005)
```

**Specialization-Based Selection:**
```python
# Find coding specialists in value tier
coding_models = selector.get_models_by_specialization("coding", "value")
# Returns: [{'name': 'qwen/qwen3-coder', 'rank': 15, ...}, ...]

# Get large context models
large_context = selector.get_large_context_models(min_context=500000)
# Returns: ['google/gemini-2.5-pro', 'openai/gpt-5', ...]
```

**Band-Based Selection:**
```python
# Select by context window band
extended_models = selector.select_models_by_context_band("extended", max_count=3)
# Returns: Models with 200K-999K token context windows

# Select by cost tier
free_models = selector.select_models_by_cost_tier("free", max_count=5)
# Returns: Top 5 free models by rank
```

## Key Features

- **Centralized configuration**: Single source of truth in models.csv and bands_config.json
- **Organizational level mapping**: Junior/senior/executive tiers with automatic cost and performance filtering
- **Specialization routing**: Coding, reasoning, vision, conversation, and general-purpose model categories
- **Dynamic band assignment**: Automatic model categorization based on quantitative criteria
- **Fallback strategies**: Cascading selection logic when primary choices are unavailable
- **Provider diversity**: Maintains balance across OpenAI, Anthropic, Google, Meta, and other providers
- **Performance optimization**: Caching and efficient lookup algorithms for sub-100ms response times
- **Schema validation**: JSON schema enforcement for data integrity and consistency
- **Cost tracking**: Automatic cost estimation for different usage patterns
- **Real-time updates**: Hot-reloading when model data or band configurations change

## Tool Parameters

**Core Selection Methods:**
- `select_consensus_models(org_level)`: Get models for consensus analysis by organizational level
- `select_layered_consensus_models(org_level)`: Get hierarchical model structure for layered consensus
- `get_best_model_for_org_role(role, org_level)`: Find optimal model for specific role and level
- `get_models_by_specialization(specialization, price_tier)`: Filter by capability and cost tier
- `get_large_context_models(min_context)`: Find models with substantial context windows

**Band-Based Selection:**
- `select_models_by_context_band(band, max_count)`: Choose by context window category
- `select_models_by_cost_tier(tier, max_count)`: Choose by pricing category
- `get_context_window_band(context_tokens)`: Determine band for token count
- `get_cost_tier_band(input_cost)`: Determine tier for pricing

## Centralized Band System

### 9 Quantitative Band Categories

**Context Window Bands:**
- **Compact**: ≤65K tokens (6-8 models)
- **Standard**: 65K-200K tokens (8-10 models)
- **Extended**: 200K-999K tokens (5-7 models)  
- **Large**: 1M+ tokens (3-4 models)

**Cost Tier Bands:**
- **Free**: $0.00 (8 models, 32% of collection)
- **Economy**: $0.01-$1.00 per million tokens (4-5 models)
- **Value**: $1.01-$10.00 per million tokens (6 models, 24%)
- **Premium**: $10.01+ per million tokens (6 models, 24%)

**Organizational Level Bands:**
- **Junior**: ≤$1 cost + ≥60 HumanEval + ≥32K context (8 models)
- **Senior**: ≤$10 cost + ≥70 HumanEval + ≥65K context (10 models)
- **Executive**: Unlimited cost + ≥80 HumanEval + ≥128K context (7 models)

**Performance Bands:**
- **Basic**: ≤65.0 HumanEval (3-4 models)
- **Good**: 65.1-75.0 HumanEval (6-8 models)
- **Excellent**: 75.1-85.0 HumanEval (8-10 models)
- **Exceptional**: 85.1+ HumanEval (4-6 models)

**Role Assignment Bands:**
- **Technical Roles**: Coding/debugging specialists → senior_developer, code_reviewer, qa_engineer
- **Architecture Roles**: Premium models ≥80 HumanEval → lead_architect, system_architect, technical_director
- **Analysis Roles**: Reasoning/security specialists → security_analyst, risk_analyst, research_lead
- **Validation Roles**: Free/economy models → technical_validator, security_checker

## Usage Examples

**Consensus Tool Integration:**
```python
# Select models for layered organizational consensus
selector = DynamicModelSelector()
layered_models, cost = selector.select_layered_consensus_models("executive")

# Result structure:
{
    "junior": ["meta-llama/llama-3.3-70b-instruct:free", "qwen/qwen3-coder:free"],
    "senior": ["anthropic/claude-sonnet-4", "openai/gpt-5-mini"],
    "executive": ["openai/gpt-5", "anthropic/claude-opus-4.1"]
}
```

**Workflow Tool Integration:**
```python
# Get best model for specific workflow role
model = selector.get_best_model_for_org_role("security_analyst", "senior")
# Returns: 'deepseek/deepseek-r1-0528' (reasoning specialist)

model = selector.get_best_model_for_org_role("lead_architect", "executive")
# Returns: 'openai/gpt-5' (premium architectural decision-making)
```

**Cost-Conscious Selection:**
```python
# Find best free models for development work
free_models = selector.get_models_by_tier("free")
coding_free = [m for m in free_models if m['specialization'] == 'coding']
# Returns: Free coding specialists like qwen/qwen-2.5-coder-32b-instruct:free
```

**Large Document Processing:**
```python
# Get models with substantial context windows
large_context = selector.get_large_context_models(min_context=1000000)
# Returns: ['google/gemini-2.5-pro', 'google/gemini-2.5-flash'] (1M+ tokens)
```

## Band Configuration Management

### Automatic Reassignment

```python
# Detect and apply band configuration changes
selector = DynamicModelSelector()

# Check for context window band changes
context_changes = selector.detect_and_apply_band_changes()

# Check for cost tier band changes
cost_changes = selector.detect_and_apply_cost_tier_changes()

# Reassign models to role bands
role_assignments = selector.reassign_models_to_role_bands()

if context_changes or cost_changes:
    print("Models automatically reassigned to new bands!")
```

### Configuration-Driven Updates

```json
// Update bands_config.json
{
  "context_window_bands": {
    "large": {"min_tokens": 1000000}  // Only change needed
  }
}

// Result: All models automatically reassign to appropriate bands
// CSV files automatically updated
// All tools immediately use new band definitions
```

## Model Classification System

**Automatic Tier Detection:**
```python
# Models automatically classified by quantitative criteria
model_data = {
    'input_cost': 3.0,
    'output_cost': 15.0,
    'humaneval_score': 88.0,
    'context_window': 400000
}

tier = selector._determine_price_tier(model_data['input_cost'])
# Returns: "premium" (based on cost thresholds)

org_level = selector._classify_org_level(model_data)
# Returns: "executive" (based on cost + performance + context)
```

**Specialization Detection:**
```python
# Automatic capability classification
if model_data.get('has_coding') or 'code' in description:
    specialization = "coding"
elif model_data.get('has_vision') or 'vision' in description:
    specialization = "vision"
# ... additional logic for reasoning, conversation, general
```

## Best Practices

- **Use organizational levels**: Request by org level rather than specific models for automatic optimization
- **Leverage specializations**: Specify task type (coding, reasoning, vision) for optimal model selection
- **Consider cost tiers**: Balance performance needs with budget constraints using tier-based selection
- **Plan for fallbacks**: The selector includes automatic fallback strategies for high availability
- **Monitor band changes**: Automatic reassignment ensures models stay optimally categorized
- **Cache efficiently**: Global instance pattern provides sub-100ms response times
- **Validate configurations**: Schema validation ensures data integrity across updates

## Integration with Other Tools

The dynamic model selector serves as the foundation for intelligent model routing across the entire system:

**Consensus Tool Integration:**
```python
# Consensus tool automatically selects diverse models
models = selector.select_layered_consensus_models("senior")
# Provides balanced representation across organizational levels
```

**Workflow Tool Integration:**
```python
# Workflow tools get optimal models for specific roles
model = selector.get_best_model_for_org_role("code_reviewer", "junior")
# Ensures appropriate model selection for task complexity
```

**Cost Optimization:**
```python
# Automatic cost-performance optimization
free_models = selector.get_models_by_tier("free")
# Prioritizes free models for development and testing
```

## Caching and Performance

**Efficient Caching Strategy:**
```python
# Class-level cache for optimal performance
_cached_models_data = None
_cache_timestamp = None
_csv_file_mtime = None

# Automatic cache invalidation on file changes
if csv_mtime != DynamicModelSelector._csv_file_mtime:
    # Reload data automatically
    self._load_cached_data()
```

**Performance Characteristics:**
- **Sub-100ms response times** for model selection queries
- **Automatic cache invalidation** when configuration files change
- **Efficient fallback cascading** with minimal computational overhead
- **Schema validation** with graceful degradation for invalid data

## Error Handling and Fallback Strategies

**Cascading Fallback Logic:**
```python
def _select_with_fallback_recovery(self, org_level):
    """Implement cascading fallback strategies"""
    
    # Fallback 1: Cross-tier selection
    all_org_models = self._get_cross_tier_models(org_level)
    if sufficient_models(all_org_models):
        return all_org_models
    
    # Fallback 2: Price-tier based selection  
    price_tier_models = self._select_by_price_tier(org_level)
    if sufficient_models(price_tier_models):
        return price_tier_models
    
    # Fallback 3: Emergency selection
    emergency_models = self._get_any_available_models()
    return emergency_models
```

**Graceful Degradation:**
- **Schema validation failures**: Continue with unvalidated data and warning
- **Missing band configurations**: Fall back to default band definitions
- **Insufficient models**: Automatic cross-tier selection with logging
- **File system errors**: Graceful error handling with meaningful messages

## When to Use Dynamic Model Selector vs Direct Model Names

- **Use `dynamic_model_selector`** for: Automatic optimization, organizational workflows, cost-conscious selection
- **Use direct model names** for: Specific testing, debugging, user preference overrides
- **Use consensus integration** for: Multi-model analysis requiring diverse perspectives
- **Use specialization filtering** for: Task-specific optimization (coding, vision, reasoning)

## Configuration Files

**models.csv Structure:**
```csv
rank,model,provider,tier,status,context,input_cost,output_cost,org_level,specialization,role,strength,humaneval_score,swe_bench_score,openrouter_url,last_updated
1,openai/gpt-5,openai,premium,paid,400K,5.0,15.0,executive,general,lead_architect,next_generation,90.0,80.0,https://openrouter.ai/openai/gpt-5,2025-08-11
```

**bands_config.json Structure:**
```json
{
  "context_window_bands": {
    "large": {
      "min_tokens": 1000000,
      "description": "Models with 1M+ token context windows"
    }
  },
  "cost_tier_bands": {
    "premium": {
      "min_cost": 10.01,
      "description": "High-performance models for critical tasks"
    }
  }
}
```

## Future Enhancements

Planned improvements for enhanced model selection capabilities:

- **Machine learning optimization**: Learn from usage patterns to improve selection algorithms
- **Real-time performance monitoring**: Adjust rankings based on actual model performance
- **Advanced cost modeling**: Dynamic pricing optimization based on usage forecasts
- **Custom scoring weights**: User-configurable importance factors for different criteria
- **Geographic optimization**: Consider regional availability and latency factors
- **Load balancing**: Distribute requests across equivalent models for better performance