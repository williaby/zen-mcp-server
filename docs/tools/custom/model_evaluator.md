# Model Evaluator Tool - AI Model Quality Assessment

**Systematically evaluate new AI models from OpenRouter URLs to determine if they should be added to your model collection**

The `model_evaluator` tool implements a quantitative framework to assess new AI models, calculating replacement scores and generating detailed recommendations with implementation plans and risk assessments.

## Thinking Mode

**Not applicable.** The model evaluator performs deterministic analysis using web scraping and mathematical scoring - no AI reasoning required for the evaluation process itself.

## Model Recommendation

The model evaluator is a standalone analysis tool that doesn't require AI model selection. It analyzes external models to help you make informed decisions about expanding your model collection.

## How It Works

The model evaluator follows a systematic 5-step process to assess new AI models:

1. **Extract metrics**: Web scrape OpenRouter pages for pricing, benchmarks, and capabilities
2. **Apply qualification filter**: Ensure models meet minimum requirements (≥32K context, ≥60 HumanEval, pricing data)
3. **Find replacement candidates**: Identify existing models that could be replaced based on tier and performance
4. **Calculate weighted scores**: Score across 4 dimensions with quantitative thresholds
5. **Generate recommendations**: Provide detailed analysis with implementation plans and CSV entries

## Example Prompts

**Evaluate Premium Model:**
```bash
python evaluate_model.py https://openrouter.ai/openai/gpt-5
```

**Check Free Model Viability:**
```bash
python evaluate_model.py https://openrouter.ai/meta-llama/llama-3.3-70b-instruct:free
```

**Generate CSV Entry Only:**
```bash
python evaluate_model.py https://openrouter.ai/anthropic/claude-opus-4.1 --csv-only
```

**Verbose Analysis:**
```bash
python evaluate_model.py https://openrouter.ai/google/gemini-2.5-pro --verbose
```

## Key Features

- **Web scraping engine**: Automatically extracts pricing, context windows, benchmarks, and capabilities from OpenRouter
- **Quantitative scoring**: 4-dimension weighted analysis (performance 40%, cost efficiency 30%, strategic value 20%, operational benefit 10%)
- **Qualification filtering**: Ensures models meet minimum standards before detailed evaluation
- **Replacement matrix**: Identifies existing models that could be replaced and calculates improvement scores
- **Implementation planning**: Generates 3-phase rollout plans with success metrics and rollback triggers
- **Risk assessment**: Evaluates potential issues and mitigation strategies
- **CSV generation**: Outputs model entries compatible with existing models.csv structure
- **Provider diversity tracking**: Considers impact on provider balance and redundancy
- **Capability detection**: Identifies multimodal, vision, coding, and reasoning specializations
- **Cost optimization**: Calculates potential savings and performance-per-dollar improvements

## Tool Parameters

**Command Line Interface:**
- `url`: OpenRouter model URL to evaluate (required)
- `--verbose`: Enable detailed progress output
- `--csv-only`: Output only CSV entry if recommended for addition

**Python API:**
- `openrouter_url`: Full OpenRouter URL (required)
- Returns: `(ModelMetrics, ReplacementRecommendation)` tuple

## Evaluation Framework

### Qualification Criteria

Models must meet **ALL** basic requirements:
- **Context Window**: ≥32,000 tokens for handling substantial documents
- **HumanEval Score**: ≥60.0 demonstrating coding capability
- **Pricing Available**: Either has defined costs or is marked as free tier
- **API Access**: Available through OpenRouter platform

### Scoring Dimensions

**Performance Analysis (40% weight):**
- HumanEval score improvements vs existing models
- SWE-bench and other benchmark comparisons
- Threshold: ≥10% improvement for replacement consideration

**Cost Efficiency (30% weight):**
- Input/output cost per million tokens analysis
- Performance-to-cost ratio calculations
- Free models receive maximum efficiency scores
- Threshold: ≥20% cost reduction OR ≥5% performance improvement

**Strategic Value (20% weight):**
- Context window capacity improvements
- New capabilities (multimodal, vision, coding specialization)
- Provider diversity impact and redundancy benefits
- Future roadmap alignment and technology advancement

**Operational Benefits (10% weight):**
- API availability and reliability track record
- Provider reputation and support quality
- Integration compatibility with existing infrastructure
- Regional availability and service level agreements

### Replacement Threshold

Models scoring **≥7.5/10** are recommended for replacement with detailed implementation guidance.

## Usage Examples

**High-Performance Model Assessment:**
```bash
python evaluate_model.py https://openrouter.ai/openai/gpt-5
# Expected: ✅ REPLACEMENT RECOMMENDED (Score: 8.5/10)
# Reasoning: Superior performance + cost efficiency + strategic value
```

**Free Model Evaluation:**
```bash
python evaluate_model.py https://openrouter.ai/meta-llama/llama-3.3-70b-instruct:free
# Expected: Depends on performance vs existing free models
# Focus: Cost efficiency (maximum) + performance comparison
```

**Specialized Model Review:**
```bash
python evaluate_model.py https://openrouter.ai/qwen/qwen3-coder
# Expected: Evaluated against existing coding specialists
# Focus: Coding benchmark performance + specialization value
```

**Integration with Model Collection:**
```bash
# Generate approved model entry
python evaluate_model.py https://openrouter.ai/anthropic/claude-opus-4.1 --csv-only >> docs/models/models.csv

# Update model selector cache
python -c "from tools.custom.dynamic_model_selector import DynamicModelSelector; DynamicModelSelector()"
```

## Output Formats

### Comprehensive Evaluation Report

```
================================================================================
MODEL EVALUATION REPORT: openai/gpt-5
================================================================================

📊 EXTRACTED METRICS
Provider: openai
HumanEval Score: 90.0
SWE-Bench Score: 80.0
Input Cost: $5.0/M tokens
Output Cost: $15.0/M tokens
Context Window: 400,000 tokens
Capabilities: multimodal, vision, coding

🎯 RECOMMENDATION
✅ REPLACEMENT RECOMMENDED
Target Model: anthropic/claude-opus-4
Replacement Score: 8.05/10
Cost Savings: 80.0%
Performance Improvement: 5.6%

💡 REASONING
Performance improvement: +5.6% on key benchmarks | Cost savings: -80.0% average cost reduction | Larger context window: 400,000 vs 200,000 tokens | Enhanced capabilities: multimodal, vision, coding

🔮 STRATEGIC BENEFITS
• Expanded context capacity for larger documents
• Added multimodal capabilities
• Reduced operational costs
• Access to latest AI technology

📋 IMPLEMENTATION PLAN
[3-phase rollout with monitoring and rollback procedures]

📄 CSV ENTRY
1,openai/gpt-5,openai,premium,paid,400K,5.0,15.0,executive,general,lead_architect,next_generation,90.0,80.0,https://openrouter.ai/openai/gpt-5,2025-08-12
```

### Model Classification System

**Automatic Tier Assignment:**
- **Free Tier**: $0 cost models with usage limits
- **Value Tier**: $0.01-$2.00 per million tokens, balanced cost/performance
- **Premium Tier**: >$2.00 per million tokens, high-performance models

**Organizational Level Mapping:**
- **Junior**: ≤$1 cost + ≥60 HumanEval + ≥32K context (development/testing)
- **Senior**: ≤$10 cost + ≥70 HumanEval + ≥65K context (professional work)
- **Executive**: Unlimited cost + ≥80 HumanEval + ≥128K context (critical decisions)

**Specialization Detection:**
- **Coding**: Programming-focused capabilities and benchmarks
- **Vision**: Multimodal/image processing capabilities
- **Reasoning**: Logic/analysis focused performance
- **Conversation**: Chat/dialogue optimization
- **General**: Broad task handling across domains

## Best Practices

- **Verify URLs**: Ensure OpenRouter URLs are current and accessible before evaluation
- **Consider context**: Evaluate models within your specific use case requirements
- **Review recommendations**: Human oversight recommended for all replacement decisions
- **Test incrementally**: Follow generated implementation plans for safe rollouts
- **Monitor performance**: Track actual vs predicted improvements post-deployment
- **Maintain diversity**: Balance provider representation and capability coverage
- **Document decisions**: Keep evaluation reports for future reference and audit trails

## Integration with Dynamic Model Selector

The model evaluator seamlessly integrates with the existing model infrastructure:

```python
# Uses same classification logic
from tools.custom.dynamic_model_selector import DynamicModelSelector
from tools.custom.model_evaluator import ModelEvaluator

# Evaluator leverages existing model data
evaluator = ModelEvaluator()
selector = evaluator.model_selector  # Access to current model collection

# Automatic band assignment using centralized configuration
price_tier = selector._determine_price_tier(model_data)
context_band = selector.get_context_window_band(context_tokens)
```

## Error Handling and Troubleshooting

**Common Issues:**

*ImportError: Model evaluation requires 'requests' and 'beautifulsoup4'*
```bash
pip install requests beautifulsoup4
```

*Model does not meet basic qualification requirements*
- Verify model has adequate context window (≥32K tokens)
- Check HumanEval score meets threshold (≥60.0)
- Ensure pricing information is available on OpenRouter

*Failed to extract metrics from URL*
- Confirm OpenRouter URL is correct and accessible
- Check network connectivity and retry
- Some models may have limited public information

*Schema validation failed*
- Warning about existing model data formatting
- Tool continues to function normally
- Does not affect evaluation accuracy

## When to Use Model Evaluator vs Other Tools

- **Use `model_evaluator`** for: Systematic assessment of new models, replacement decisions, cost-benefit analysis
- **Use `consensus`** for: Multi-perspective analysis of evaluation results, stakeholder alignment
- **Use `chat`** for: Discussing model selection strategy and requirements
- **Use `analyze`** for: Understanding existing model performance and usage patterns

## Future Enhancements

Planned improvements for enhanced evaluation capabilities:

- **Automated benchmark testing**: Run actual performance tests on candidate models
- **Real-time pricing monitoring**: Track OpenRouter price changes and model availability
- **Batch evaluation**: Process multiple models simultaneously for comparative analysis
- **Historical performance tracking**: Monitor model quality evolution over time
- **A/B testing integration**: Generate controlled rollout plans with statistical validation
- **Custom scoring weights**: Adjust evaluation criteria for specific use cases