# QuickReview Tool - Fast Zero-Cost Validation

**Get quick validation feedback using free models only for basic syntax, logic, and documentation checking**

The `quickreview` tool provides fast, zero-cost basic validation using 2-3 free models with simple role-based analysis. Perfect for grammar and syntax checking, basic code validation, documentation review, and simple logic verification when you need quick feedback without premium model costs.

## Thinking Mode

**Low thinking mode.** QuickReview uses minimal thinking depth (low) to optimize for speed and fast results, making it ideal for frequent validation tasks during development.

## Model Recommendation

QuickReview automatically selects from free-tier models only to maintain zero cost operation while providing reliable basic validation. Models are chosen for availability, basic technical competency, and cost optimization.

## How It Works

QuickReview provides fast validation through a streamlined approach:

1. **Free model selection**: Automatically chooses 2-3 available free models from the curated list
2. **Simple role assignment**: Assigns basic validation roles (syntax checker, logic reviewer, docs checker)
3. **Zero-cost operation**: Maintains $0.00 cost through exclusive use of free models
4. **3-step workflow**: Optimized workflow for speed (analysis → consultation → synthesis)
5. **Self-contained execution**: No external expert analysis needed - completes with free model consultations

## Example Prompts

**Code Syntax Checking:**
```
zen quickreview "Check this Python code for syntax errors" --focus syntax
```

**Documentation Review:**
```
zen quickreview "Review this README for clarity and completeness" --focus docs
```

**Basic Logic Validation:**
```
zen quickreview "Validate the logic flow in this function" --focus logic
```

**General Validation:**
```
zen quickreview "Check this code for obvious issues and improvements"
```

## Key Features

- **Zero-cost operation**: Uses only free models to eliminate analysis costs completely
- **Fast execution**: Streamlined 3-step workflow optimized for speed
- **Simple role-based analysis**: Syntax checker, logic reviewer, documentation checker roles
- **Automatic model selection**: Intelligent fallback when preferred free models are unavailable
- **Development-focused**: Optimized for frequent use during development without budget concerns
- **Self-contained**: No external dependencies or expert analysis - completes independently
- **Focus area targeting**: Optional focus on specific validation aspects (syntax, logic, docs, general)
- **Transparent operation**: Shows exactly which free models and roles were used

## Tool Parameters

**Required:**
- `proposal`: What to review or validate - be specific about what you want checked (required)

**Optional:**
- `focus`: Focus area for validation - "syntax", "logic", "docs", or "general" (defaults to "general")

**Automatic Configuration:**
- Models: 2-3 free models selected automatically based on availability
- Roles: Simple validation roles assigned automatically
- Cost: $0.00 (free models only, no paid fallback)
- Workflow: 3 steps (analysis → consultation → synthesis)

## Focus Areas

### Syntax Focus (`--focus syntax`)
- **Grammar and formatting**: Basic syntax, grammar, formatting, and obvious errors
- **Style consistency**: Consistent formatting and basic style compliance
- **Structural validation**: Proper structure and organization
- **Error identification**: Clear syntax errors and formatting issues

### Logic Focus (`--focus logic`)
- **Basic logic flow**: Logic flow, consistency, and simple correctness issues
- **Flow validation**: Control flow and basic algorithmic correctness
- **Consistency checking**: Logical consistency and coherence
- **Simple correctness**: Obvious logical errors and improvements

### Documentation Focus (`--focus docs`)
- **Clarity assessment**: Documentation clarity, completeness, and accuracy
- **Completeness evaluation**: Missing information and coverage gaps
- **Accuracy checking**: Factual correctness and up-to-date information
- **Readability improvement**: Writing quality and user experience

### General Focus (`--focus general` - default)
- **Overall validation**: Comprehensive basic validation across all areas
- **Multi-aspect checking**: Syntax, logic, and documentation combined
- **Balanced analysis**: Equal attention to all validation aspects
- **Holistic assessment**: Overall quality and improvement opportunities

## Usage Examples

**Python Code Syntax Check:**
```
zen quickreview "Check this Python function for syntax errors" --focus syntax

# Expected analysis:
# Syntax Checker: Identifies missing colons, indentation issues, variable naming
# Logic Reviewer: Checks basic flow and obvious logical problems
# Documentation Checker: Reviews code comments and docstring clarity
```

**Documentation Review:**
```
zen quickreview "Review this API documentation for clarity" --focus docs

# Expected analysis:
# Documentation Checker: Evaluates clarity, completeness, accuracy, examples
# Syntax Checker: Checks formatting, markdown syntax, structure
# Logic Reviewer: Validates logical flow and organization of information
```

**Code Logic Validation:**
```
zen quickreview "Validate the algorithm logic in this sorting function" --focus logic

# Expected analysis:
# Logic Reviewer: Evaluates algorithmic correctness, edge cases, efficiency
# Syntax Checker: Identifies any syntax issues affecting logic
# Documentation Checker: Reviews comments explaining the logic
```

**General Code Review:**
```
zen quickreview "Quick review of this component implementation"

# Expected analysis:
# All three roles provide balanced feedback across syntax, logic, and documentation
# Comprehensive basic validation suitable for development checkpoints
```

## Free Model Strategy

### Primary Free Models

QuickReview prioritizes the best available free models:

**Priority Selection:**
- `deepseek/deepseek-r1-distill-llama-70b:free` (Best free reasoning model)
- `meta-llama/llama-3.1-405b-instruct:free` (Largest free model, 80.5% HumanEval)
- `qwen/qwen-2.5-coder-32b-instruct:free` (Free coding specialist)

**Fallback Options:**
- `meta-llama/llama-4-maverick:free` (Latest Meta architecture)
- `meta-llama/llama-3.3-70b-instruct:free` (Efficient 70B performance)
- `qwen/qwen2.5-vl-72b-instruct:free` (Vision-language capabilities)
- `microsoft/phi-4-reasoning:free` (Debugging specialist)
- `qwen/qwq-32b:free` (Free reasoning model)
- `moonshotai/kimi-k2:free` (Alternative provider)

### Availability Handling

**Dynamic Selection:**
- Attempts priority models first for best quality
- Falls back through extended free model list
- Requires minimum 1 model, warns if fewer than 2 available
- Handles provider outages gracefully
- Never exceeds $0.00 budget (no paid fallbacks)

## Workflow Structure

### 3-Step Streamlined Process

**Step 1: Initial Analysis + First Model Consultation**
- Analyze the validation request
- Examine provided files if any
- Consult first selected free model
- Prepare for remaining consultations

**Step 2: Model Consultations**
- Consult remaining free models (typically 1-2 additional)
- Gather validation feedback from each model
- Apply focus-specific role guidance
- Collect diverse perspectives

**Step 3: Final Synthesis**
- Synthesize all free model feedback
- Provide clear, actionable recommendations
- Highlight any issues requiring deeper analysis
- Complete validation with practical suggestions

### Cost and Time Optimization

```
QUICKREVIEW COMPLETE

Cost: $0.00 (free models only)
Models Consulted: 3 free models
Time: ~30-60 seconds (optimized for speed)
Focus: general validation
Tool: quickreview

MODEL DETAILS:
- deepseek/deepseek-r1-distill-llama-70b:free (syntax_checker)
- meta-llama/llama-3.1-405b-instruct:free (logic_reviewer)  
- qwen/qwen-2.5-coder-32b-instruct:free (docs_checker)
```

## Role Assignment

### Simple Validation Roles

**Syntax Checker:**
- Focus: Basic syntax, grammar, formatting, and obvious errors
- Expertise: Code syntax, markdown formatting, style consistency
- Output: Clear identification of syntax issues with specific examples

**Logic Reviewer:**
- Focus: Basic logic flow, consistency, and simple correctness issues
- Expertise: Control flow, algorithmic logic, logical consistency
- Output: Logic flow analysis with improvement suggestions

**Documentation Checker:**
- Focus: Documentation clarity, completeness, and accuracy
- Expertise: Technical writing, documentation standards, user experience
- Output: Documentation quality assessment with readability improvements

### Role Assignment Strategy

**Focus-Based Priority:**
- If specific focus provided, prioritize that role for first model
- Remaining models get complementary roles for balanced coverage
- General focus distributes roles evenly across all aspects

**Model-Role Matching:**
- Coding specialists (qwen coder) often assigned to syntax checking
- Reasoning models (deepseek) typically handle logic review
- General models handle documentation or balanced analysis

## Best Practices

- **Use for frequent validation**: Perfect for regular development checkpoints without cost concerns
- **Quick development feedback**: Get fast feedback during coding sessions
- **Pre-review validation**: Validate code before requesting formal code review
- **Documentation drafts**: Quick checks on documentation clarity and completeness
- **Learning and exploration**: Safe environment for getting basic validation feedback
- **CI/CD integration**: Zero-cost validation in automated workflows
- **Iterative improvement**: Use repeatedly to refine code, docs, or logic incrementally

## Integration with Development Workflow

### Development Scripts

```bash
#!/bin/bash
# Development validation helper
echo "Running quick validation on: $1"
zen quickreview "Quick review of recent changes" --focus general
```

### IDE Integration

```bash
# Quick syntax check shortcut
alias qsyntax='zen quickreview "Check for syntax errors" --focus syntax'
alias qlogic='zen quickreview "Validate logic flow" --focus logic' 
alias qdocs='zen quickreview "Review documentation" --focus docs'
```

### CI/CD Pipeline

```yaml
# Example GitHub Actions integration
- name: Quick validation check
  run: |
    zen quickreview "Validate changes for obvious issues" \
      --focus general --files "$(git diff --name-only HEAD~1)"
```

## Error Handling and Resilience

**Model Availability Issues:**
- Graceful degradation through free model priority list
- Clear messaging when preferred models unavailable
- Continues with any available free models
- Helpful guidance when no free models available

**Validation Scope Limitations:**
- Clear communication about basic validation scope
- Recommendations for deeper analysis when needed
- Acknowledgment of free model capability constraints
- Guidance for escalating to professional tools when appropriate

**File Handling:**
- Robust file reading and content processing
- Graceful handling of large files or missing files
- Clear error messages for file access issues
- Appropriate content truncation for model limits

## When to Use QuickReview vs Other Tools

- **Use `quickreview`** for: Quick validation, development feedback, syntax checks, free analysis
- **Use `basic_consensus`** for: Development decisions requiring multiple perspectives, consensus analysis
- **Use `review_consensus`** for: Professional analysis, production decisions, comprehensive feedback
- **Use `critical_consensus`** for: Strategic decisions, enterprise analysis, maximum capability
- **Use `layered_consensus`** for: Organizational perspectives, hierarchical analysis, cost-controlled comprehensive coverage

## Limitations and Scope

### Validation Scope

**What QuickReview Handles Well:**
- Basic syntax and formatting errors
- Obvious logic flow issues
- Documentation clarity and completeness
- Simple correctness problems
- Style consistency checking

**What Requires Premium Tools:**
- Complex architectural analysis
- Security vulnerability assessment
- Performance optimization analysis
- Strategic technology decisions
- Enterprise-level risk assessment

### Free Model Constraints

**Capability Boundaries:**
- Basic technical competency vs advanced reasoning
- Obvious issues vs subtle problems
- Simple validation vs comprehensive analysis
- Fast feedback vs thorough investigation

**Quality Expectations:**
- Reliable for common issues and clear problems
- May miss subtle or complex problems
- Best effort within free model capabilities
- Transparent about scope limitations

## Technical Implementation

### Self-Contained Architecture

QuickReview is completely self-contained to avoid merge conflicts:

**Isolated Implementation:**
- Standalone tool in `/tools/custom/` directory
- No dependencies on external prompt files
- Self-contained system prompts and role definitions
- Independent workflow management

**Plugin-Style Integration:**
- Automatic discovery and registration
- Zero-conflict development approach
- Independent testing and validation
- Minimal core system integration

### Performance Optimization

**Speed-Focused Design:**
- Low temperature (0.2) for consistent results
- Minimal thinking mode for fast execution
- Streamlined 3-step workflow
- Optimized prompt structure for quick processing

**Resource Efficiency:**
- Free model prioritization for zero cost
- Efficient model consultation process
- Minimal context usage for faster responses
- Lightweight workflow management

This tool provides developers with fast, cost-free validation feedback perfect for regular development activities while maintaining clear boundaries about its scope and capabilities.