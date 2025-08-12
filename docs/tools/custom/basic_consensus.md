# Basic Consensus Tool - Junior Developer Level Analysis

**Get consensus from junior developer perspective using free models and entry-level roles**

The `basic_consensus` tool simulates getting technical input from junior developers and interns, using cost-effective free models with basic validation roles appropriate for development-level decision making.

## Thinking Mode

**Not applicable.** Basic consensus uses predetermined free models and junior-level roles - the underlying consensus analysis handles any required reasoning at the model level.

## Model Recommendation

Basic consensus automatically selects from free-tier models to keep costs at zero while providing reliable entry-level technical validation. Models are chosen for availability and basic technical competency.

## How It Works

Basic consensus provides junior developer level analysis through a structured approach:

1. **Free model selection**: Automatically chooses 3 available free models from the curated list
2. **Entry-level roles**: Assigns basic professional roles appropriate for junior developers
3. **Cost-conscious analysis**: Maintains zero or minimal cost while providing technical validation
4. **Consensus orchestration**: Uses the core consensus engine with junior-appropriate parameters
5. **Transparent reporting**: Shows which models and roles were used for full transparency

## Example Prompts

**Development Decision:**
```
zen basic_consensus "Should we use React or Vue for our new component library?"
```

**Code Review Request:**
```
zen basic_consensus "Is this authentication implementation secure enough for our MVP?"
```

**Technical Feasibility:**
```
zen basic_consensus "Can we implement real-time chat with our current tech stack?"
```

**Library Evaluation:**
```
zen basic_consensus "Should we adopt this new testing framework for our project?"
```

## Key Features

- **Zero-cost operation**: Uses only free models to eliminate analysis costs
- **Junior-level roles**: Code Reviewer, Security Checker, Technical Validator roles
- **Automatic model selection**: Intelligent fallback if preferred free models are unavailable
- **Development-focused**: Optimized for day-to-day development decisions and code reviews
- **Fast execution**: Streamlined analysis appropriate for frequent development use
- **Transparent operation**: Shows exactly which free models and roles were assigned
- **Organizational realism**: Mirrors actual junior developer authority and expertise levels
- **Integration ready**: Works seamlessly with development workflows and CI/CD processes

## Tool Parameters

**Required:**
- `proposal`: The question or technical decision to analyze (required)

**Automatic Configuration:**
- Models: 3 free models selected automatically based on availability
- Roles: Junior-level roles assigned automatically (Code Reviewer, Security Checker, Technical Validator)
- Cost: $0.00-0.50 budget range (free models preferred, cheap paid fallback if needed)
- Organizational Level: Junior Developer/Intern authority level

## Role Assignment

### Junior Developer Professional Roles

**Code Reviewer (Supportive Stance):**
- Focus: Basic code quality and syntax checking
- Perspective: Looks for obvious improvements and standard practices
- Authority Level: Entry-level code review and quality validation

**Security Checker (Critical Stance):**
- Focus: Obvious security issues and common vulnerabilities
- Perspective: Identifies clear security problems and basic best practices
- Authority Level: Junior-level security awareness and basic vulnerability detection

**Technical Validator (Neutral Stance):**
- Focus: Basic technical feasibility and logic validation
- Perspective: Assesses whether approach is technically sound and implementable
- Authority Level: Entry-level technical feasibility and basic architecture understanding

## Usage Examples

**Feature Development Decision:**
```
zen basic_consensus "Should we implement user authentication with OAuth or build custom login?"

# Expected analysis:
# - Code Reviewer: Evaluates implementation complexity and maintainability
# - Security Checker: Identifies OAuth security benefits vs custom risks
# - Technical Validator: Assesses technical feasibility and integration requirements
```

**Code Structure Review:**
```
zen basic_consensus "Is our current folder structure good for a React project, or should we reorganize?"

# Expected analysis:
# - Code Reviewer: Evaluates folder organization against React best practices
# - Security Checker: Identifies any structure-related security considerations
# - Technical Validator: Assesses impact on build system and development workflow
```

**Technology Choice:**
```
zen basic_consensus "Should we use TypeScript for our new JavaScript project?"

# Expected analysis:
# - Code Reviewer: Evaluates code quality and maintainability benefits
# - Security Checker: Considers type safety security implications
# - Technical Validator: Assesses learning curve and development impact
```

**Third-Party Integration:**
```
zen basic_consensus "Should we integrate Stripe for payments or use our existing payment processor?"

# Expected analysis:
# - Code Reviewer: Evaluates integration complexity and code maintainability
# - Security Checker: Compares security implications of both approaches
# - Technical Validator: Assesses technical feasibility and migration effort
```

## Cost and Budget Management

### Free Model Strategy

Basic consensus prioritizes cost optimization through intelligent free model selection:

**Primary Free Models:**
- `deepseek/deepseek-r1-distill-llama-70b:free` (Best free reasoning model)
- `meta-llama/llama-3.1-405b-instruct:free` (Largest free model, 80.5% HumanEval)
- `qwen/qwen-2.5-coder-32b-instruct:free` (Free coding specialist)

**Fallback Strategy:**
- If preferred free models unavailable, selects from extended free model list
- Emergency fallback to low-cost paid models if no free models available
- Never exceeds $0.50 budget appropriate for junior developer decisions

### Cost Transparency

```
JUNIOR CONSENSUS COMPLETE

Organizational Level: Junior Developer / Intern Level
Models Used: 3 models (free preferred, cheap paid fallback)
Roles Assigned: Code Reviewer (basic), Security Checker (obvious issues), Technical Validator (simple feasibility)
Cost: Junior developer budget (typically $0.00-0.50)
Tool: basic_consensus

MODEL SELECTION DETAILS:
Orchestrator Model: anthropic/claude-sonnet-4
Consensus Models: deepseek/deepseek-r1-distill-llama-70b:free, meta-llama/llama-3.1-405b-instruct:free, qwen/qwen-2.5-coder-32b-instruct:free
Total Models: 3 consensus + 1 orchestrator
```

## Best Practices

- **Use for development decisions**: Perfect for day-to-day technical choices during development
- **Quick validation needs**: When you need fast, cost-free technical validation
- **Code review situations**: Get multiple perspectives on code quality and basic security
- **Learning and exploration**: Safe environment for junior developers to get technical input
- **Frequent decision making**: Use liberally since cost is minimal or zero
- **MVP and prototype decisions**: Appropriate authority level for early-stage technical choices
- **Team development**: Help junior team members understand different perspectives on technical decisions

## Integration with Development Workflow

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Get basic consensus on architecture changes
  run: |
    zen basic_consensus "Should we proceed with this refactoring approach?" \
      --files changed_files.txt
```

### Development Scripts

```bash
#!/bin/bash
# Development decision helper
echo "Getting junior developer consensus on: $1"
zen basic_consensus "$1"
```

### Code Review Process

```bash
# Pre-review consensus check
zen basic_consensus "Is this pull request ready for senior developer review?" \
  --files "$(git diff --name-only HEAD~1)"
```

## Error Handling and Fallbacks

**Model Availability Issues:**
- Automatic fallback through free model priority list
- Graceful degradation to available models
- Clear messaging when fallback models are used

**Insufficient Free Models:**
- Emergency selection of low-cost paid models within budget
- Warning messages about cost implications
- Maintains $0.50 maximum budget constraint

**Analysis Failures:**
- Comprehensive error reporting with recovery suggestions
- Integration with shared error handling from `ConsensusToolBase`
- Helpful guidance for retrying with different parameters

## When to Use Basic Consensus vs Other Tools

- **Use `basic_consensus`** for: Development decisions, code reviews, MVP choices, frequent validation needs
- **Use `review_consensus`** for: Production decisions, architectural reviews, senior-level analysis needs
- **Use `critical_consensus`** for: Strategic decisions, enterprise choices, executive-level analysis
- **Use `layered_consensus`** for: Comprehensive analysis requiring multiple organizational perspectives
- **Use `quickreview`** for: Pure validation tasks (syntax, logic) without consensus analysis

## Organizational Context

Basic consensus represents the first tier in the organizational decision-making hierarchy:

**Junior Developer Authority Level:**
- Code quality and basic architecture decisions
- Technology choices for development and testing
- Third-party library and framework selection for non-critical systems
- Development workflow and tooling decisions
- Code structure and organization choices

**Appropriate Decision Scope:**
- Individual feature implementations
- Development environment setup
- Testing strategies and frameworks
- Code organization and structure
- Basic security practices and validation

**Budget Alignment:**
- Matches financial authority of junior developers and interns
- Cost-conscious approach appropriate for frequent use
- Zero or minimal cost enables regular decision support without budget concerns