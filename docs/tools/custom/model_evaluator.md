# Model Evaluator Tool

A comprehensive tool for evaluating new AI models from OpenRouter URLs to determine if they should be added to the Zen MCP Server model collection.

## Overview

The Model Evaluator implements the quantitative framework defined in `docs/models/model_selection_framework.md` to:

1. **Extract model metrics** from OpenRouter URLs using web scraping
2. **Apply qualification criteria** to filter out unsuitable models
3. **Calculate replacement scores** using weighted scoring across 4 dimensions
4. **Generate detailed recommendations** with implementation plans and risk assessments
5. **Output CSV entries** compatible with the existing models.csv structure

## Installation

Required packages:
```bash
pip install requests beautifulsoup4
```

## Usage

### Command Line Interface

```bash
# Basic evaluation
python evaluate_model.py https://openrouter.ai/ai21/jamba-large-1.7

# Verbose output with detailed progress
python evaluate_model.py https://openrouter.ai/openai/gpt-5 --verbose

# CSV-only output (for automation)
python evaluate_model.py https://openrouter.ai/anthropic/claude-opus-4.1 --csv-only
```

### Python API

```python
from tools.custom.model_evaluator import ModelEvaluator

# Initialize evaluator
evaluator = ModelEvaluator()

# Evaluate a model from URL
model_metrics, recommendation = evaluator.evaluate_model_from_url(
    'https://openrouter.ai/openai/gpt-5'
)

# Print comprehensive report
evaluator.print_evaluation_report(model_metrics, recommendation)

# Generate CSV entry for models.csv
if recommendation.should_replace:
    csv_entry = evaluator.generate_csv_entry(model_metrics)
    print(csv_entry)
```

## Evaluation Framework

### Qualification Criteria

Models must meet ALL basic requirements:
- **Context Window**: ≥32,000 tokens
- **HumanEval Score**: ≥60.0 (coding capability)
- **Pricing Available**: Either has costs or is marked as free
- **API Access**: Available through OpenRouter

### Scoring Dimensions

The tool calculates a weighted replacement score across 4 dimensions:

#### 1. Performance (40% weight)
- HumanEval score improvements
- SWE-bench score improvements  
- MMLU and other benchmark scores
- **Threshold**: ≥10% improvement for replacement

#### 2. Cost Efficiency (30% weight)
- Input/output cost per million tokens
- Performance-to-cost ratio analysis
- Free models get maximum cost efficiency score
- **Threshold**: ≥20% cost reduction OR ≥5% performance improvement

#### 3. Strategic Value (20% weight)
- Context window improvements
- New capabilities (multimodal, vision, coding)
- Provider diversity impact
- Future roadmap alignment

#### 4. Operational Benefits (10% weight)
- API availability and reliability
- Provider track record
- Integration compatibility
- Regional availability

### Replacement Threshold

Models with a **total score ≥7.5/10** are recommended for replacement.

## Output Formats

### Comprehensive Report

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
[Detailed 3-phase rollout plan with success metrics and rollback triggers]

📄 CSV ENTRY
1,openai/gpt-5,openai,premium,paid,400K,5.0,15.0,executive,general,lead_architect,next_generation,90.0,80.0,https://openrouter.ai/openai/gpt-5,2025-08-12
```

### CSV-Only Output

```bash
python evaluate_model.py https://openrouter.ai/openai/gpt-5 --csv-only
# Output: 1,openai/gpt-5,openai,premium,paid,400K,5.0,15.0,executive,general,lead_architect,next_generation,90.0,80.0,https://openrouter.ai/openai/gpt-5,2025-08-12
```

## Model Classification

The tool automatically classifies models across multiple dimensions:

### Price Tiers
- **Free**: $0 cost models
- **Value**: $0.01-$2.00 per million tokens
- **Premium**: >$2.00 per million tokens

### Organizational Levels
- **Junior**: ≤$1 cost + ≥60 HumanEval + ≥32K context
- **Senior**: ≤$10 cost + ≥70 HumanEval + ≥65K context  
- **Executive**: Unlimited cost + ≥80 HumanEval + ≥128K context

### Specializations
- **Coding**: Code/programming focused capabilities
- **Vision**: Multimodal/image processing capabilities
- **Reasoning**: Logic/analysis focused capabilities
- **Conversation**: Chat/dialogue optimization
- **General**: Broad task handling

### Roles
- Technical roles: `code_reviewer`, `senior_developer`, `qa_engineer`
- Architecture roles: `lead_architect`, `system_architect`, `technical_director`
- Analysis roles: `security_analyst`, `risk_analyst`, `research_lead`
- Validation roles: `technical_validator`, `security_checker`

### Strength Classifications
- **Next Generation**: ≥88 HumanEval flagship models
- **Advanced**: ≥85 HumanEval professional-grade models
- **Balanced**: ≥75 HumanEval well-rounded models
- **Efficient**: High performance-to-cost ratio models
- **Specialized**: Domain-specific capabilities

## Web Scraping Strategy

The tool extracts metrics from OpenRouter pages using:

### Pricing Extraction
```python
# Patterns for input/output cost detection
pricing_patterns = [
    r'\$([0-9.]+).*?input.*?million',
    r'input.*?\$([0-9.]+).*?million',
    r'\$([0-9.]+).*?1M.*?tokens'
]
```

### Context Window Detection
```python
# Patterns for context window extraction
patterns = [
    r'([0-9,]+)\s*(?:K|k).*?context',
    r'([0-9.]+)\s*(?:M|m).*?context'
]
```

### Performance Benchmarks
```python
# Extract benchmark scores when available
benchmark_pattern = rf'{benchmark_name}[:\s]*([0-9.]+)%?'
```

### Capability Detection
```python
# Detect capabilities from page content
page_text = soup.get_text().lower()
has_multimodal = any(term in page_text for term in ['multimodal', 'vision', 'image'])
has_coding = any(term in page_text for term in ['code', 'coding', 'programming'])
```

## Integration with Dynamic Model Selector

The evaluator integrates seamlessly with the existing `DynamicModelSelector`:

```python
# Use existing model data for comparison
self.model_selector = DynamicModelSelector()
existing_models = self.model_selector.models_data

# Apply same classification logic
price_tier = self.model_selector._determine_price_tier(model_data)
context_band = self.model_selector.get_context_window_band(context_tokens)
```

## Error Handling

The tool includes robust error handling:

### Web Scraping Failures
- Graceful degradation when metrics can't be extracted
- Conservative estimates for missing performance data
- Fallback to basic model information from URL parsing

### Missing Dependencies
- Clear error messages for missing packages
- Guidance for installing required dependencies

### Invalid URLs
- URL validation and parsing
- Helpful error messages for malformed OpenRouter URLs

## Configuration

The tool uses configuration from the model selection framework:

```python
framework_config = {
    "provider_limits": {
        "max_models_per_provider": 6,
        "minimum_providers": 4
    },
    "minimum_benchmarks": {
        "humaneval": 60.0,
        "swe_bench": 45.0,
        "mmlu": 70.0
    },
    "replacement_threshold": 7.5,
    "scoring_weights": {
        "performance": 0.4,
        "cost_efficiency": 0.3,
        "strategic_value": 0.2,
        "operational_benefit": 0.1
    }
}
```

## Examples

### High-Performance Model (Recommended)
```bash
python evaluate_model.py https://openrouter.ai/openai/gpt-5
# Result: ✅ REPLACEMENT RECOMMENDED (Score: 8.5/10)
```

### Free Model (May Not Qualify)
```bash  
python evaluate_model.py https://openrouter.ai/ai21/jamba-large-1.7
# Result: ❌ REPLACEMENT NOT RECOMMENDED (Below performance threshold)
```

### CSV Integration
```bash
# Generate CSV entry for approved model
python evaluate_model.py https://openrouter.ai/anthropic/claude-opus-4.1 --csv-only >> docs/models/models.csv
```

## Future Enhancements

Potential improvements for the tool:

1. **Automated benchmark testing** - Run actual performance tests
2. **Real-time pricing updates** - Monitor OpenRouter for price changes  
3. **Batch evaluation** - Process multiple models simultaneously
4. **Integration with CI/CD** - Automated model discovery and evaluation
5. **Historical tracking** - Track model performance over time
6. **A/B testing support** - Generate controlled rollout plans

## Troubleshooting

### Common Issues

**ImportError: Model evaluation requires 'requests' and 'beautifulsoup4'**
```bash
pip install requests beautifulsoup4
```

**Schema validation failed**
- This is a warning about existing model data formatting
- Tool continues to work normally
- Can be ignored for evaluation purposes

**Model does not meet basic qualification requirements**
- Check that the model has adequate context window (≥32K)
- Verify HumanEval score meets minimum threshold (≥60)
- Ensure pricing information is available

**Failed to extract metrics from URL**
- Verify the OpenRouter URL is correct and accessible
- Check internet connectivity
- Try again as OpenRouter pages may be temporarily unavailable

This tool provides a systematic, data-driven approach to model evaluation that aligns with the Zen MCP Server's quantitative framework for maintaining a high-quality, cost-effective model collection.

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