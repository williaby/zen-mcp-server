# Protected Model Examples: Strategic Replacement Logic

## Example 1: Same-Generation Upgrade (Opus 4 -> Opus 4.1)

### Scenario
Anthropic releases Claude Opus 4.1 as an upgrade to Opus 4 with minor performance improvements but no cost increase.

### Input Data
```python
existing_model = ModelMetrics(
    name="anthropic/claude-opus-4",
    provider="anthropic",
    humaneval_score=85.2,
    mmlu_score=86.1,
    output_cost=75.0,  # $75/M tokens
    context_window=200000
)

new_model = ModelMetrics(
    name="anthropic/claude-opus-4.1", 
    provider="anthropic",
    humaneval_score=86.1,  # +1.1% improvement
    mmlu_score=86.8,       # +0.8% improvement  
    output_cost=75.0,      # Same cost
    context_window=200000
)
```

### Analysis Result
```python
# Detected as same-generation upgrade
is_same_generation = True
is_protected_provider = True

# Special scoring applied
score_breakdown = {
    "performance": 8.0,      # High score for any measurable improvement
    "cost_efficiency": 9.0,  # High score for no cost increase
    "strategic_value": 8.0,  # High score for staying current  
    "operational_benefit": 7.0  # Good score for version currency
}

weighted_score = (8.0 * 0.4) + (9.0 * 0.3) + (8.0 * 0.2) + (7.0 * 0.1) = 8.2/10
```

**Result**: ✅ **AUTOMATIC REPLACEMENT APPROVED** (Score: 8.2 ≥ 7.5)

**Reasoning**: "Same-generation upgrade with no cost increase and measurable performance improvements - automatic approval per protected model policy"

---

## Example 2: Cross-Generation Replacement (GPT-5 replacing multiple GPT-4 models)

### Scenario
OpenAI releases GPT-5 to replace their GPT-4 series, including deprecated models GPT-4, GPT-4 Turbo, and o3 (assuming o3 was part of GPT-4 family).

### Current OpenAI Models in Set
```python
current_openai_models = [
    {"name": "openai/gpt-4", "rank": 8, "status": "deprecated"},
    {"name": "openai/gpt-4-turbo", "rank": 6, "status": "deprecated"}, 
    {"name": "openai/o3", "rank": 4, "status": "deprecated"},
    {"name": "openai/gpt-4-mini", "rank": 12, "status": "active"},
    {"name": "openai/dall-e-3", "rank": 15, "status": "active"}  # Specialized
]
```

### GPT-5 Analysis
```python
new_model = ModelMetrics(
    name="openai/gpt-5",
    provider="openai",
    humaneval_score=90.0,    # Major improvement over GPT-4 (75.2)
    mmlu_score=88.5,         # Major improvement
    output_cost=15.0,        # Reduced from GPT-4's 30.0
    context_window=400000    # Doubled from 200K
)
```

### Replacement Strategy
Based on cross-generation replacement rules:

#### Replace Multiple Models (Allowed: max 4 per provider)
1. **openai/gpt-4** → Replaced by GPT-5 ✅
2. **openai/gpt-4-turbo** → Replaced by GPT-5 ✅  
3. **openai/o3** → Replaced by GPT-5 ✅

#### Keep Strategic Models
- **openai/gpt-4-mini** → Retained (cost-effective option)
- **openai/dall-e-3** → Retained (specialized multimodal)

### Quantitative Analysis per Replaced Model

#### GPT-4 Replacement
```python
score_breakdown = {
    "performance": 9.5,      # 19.7% HumanEval improvement
    "cost_efficiency": 8.5,  # 50% cost reduction  
    "strategic_value": 9.0,  # Next-generation capability
    "operational_benefit": 8.0  # Better reliability expected
}
weighted_score = 9.0/10
```

#### GPT-4-Turbo Replacement  
```python
score_breakdown = {
    "performance": 8.2,      # 15.1% improvement
    "cost_efficiency": 7.8,  # 40% cost reduction
    "strategic_value": 9.0,  # Consolidation benefit
    "operational_benefit": 8.0
}
weighted_score = 8.3/10
```

#### o3 Replacement
```python 
score_breakdown = {
    "performance": 7.9,      # 12.8% improvement  
    "cost_efficiency": 8.9,  # 60% cost reduction
    "strategic_value": 8.5,  # Model consolidation
    "operational_benefit": 8.0
}
weighted_score = 8.2/10
```

**All scores ≥ 7.5 → ✅ REPLACEMENT APPROVED for all three models**

### Final Model Set Impact

#### Before GPT-5 (5 OpenAI models):
- gpt-4, gpt-4-turbo, o3, gpt-4-mini, dall-e-3

#### After GPT-5 (3 OpenAI models):
- **gpt-5** (replaces 3 deprecated models), gpt-4-mini, dall-e-3

#### Benefits:
- **Simplified portfolio**: 5 → 3 OpenAI models
- **Cost savings**: Average 50% reduction across replaced models
- **Performance gain**: 15%+ improvement in key benchmarks
- **Strategic positioning**: Latest generation technology
- **Maintained coverage**: Cost-effective and specialized options retained

---

## Framework Protection Logic Summary

### Protected Model Rules Applied:

#### Tier 1 Providers (OpenAI, Anthropic, Google):
- **Always retain 2 best models** from each provider
- **Same-generation upgrades**: Replace if no cost increase (any performance gain)
- **Cross-generation**: May replace up to 4 models per provider
- **End-of-life priority**: Deprecated models become primary replacement targets

#### Replacement Hierarchy:
1. **Deprecated/EOL models** (highest priority for replacement)
2. **Older generation models** with significant performance gaps
3. **Redundant models** in same capability category
4. **Cost-inefficient models** relative to newer options

#### Never Replace Without Approval:
- **Top 2 performing models** from Tier 1 providers
- **Unique capability models** (only multimodal, only free tier, etc.)
- **Strategic partnerships** (specialized integrations)

This approach ensures you maintain the best models from key providers while allowing strategic evolution of your model portfolio through automated, quantitative analysis.