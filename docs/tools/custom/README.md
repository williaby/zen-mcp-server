# Custom Tools - Organizational Decision Framework

**Specialized tools for organizational-level decision making and model evaluation**

The custom tools directory provides an organizational decision-making framework that mirrors real IT hierarchies, enabling appropriate model selection based on decision importance, budget constraints, and organizational authority levels.

## Organizational Consensus Framework

### Decision-Making Hierarchy

The consensus tools implement a realistic organizational structure for technical decision-making:

**Junior Developer Level** → **Senior Staff Level** → **Executive Leadership Level**

Each level uses appropriate models, budgets, and roles that match real-world organizational responsibilities.

### Tool Overview

| Tool | Organizational Level | Cost Range | Models Used | Use Cases |
|------|---------------------|-------------|-------------|-----------|
| **`basic_consensus`** | Junior Developer | $0.00-0.50 | 3 free models | Development decisions, code reviews, basic validation |
| **`review_consensus`** | Senior Staff | $1.00-5.00 | 5 professional models | Production decisions, architecture reviews, system design |
| **`critical_consensus`** | Executive Leadership | $5.00-25.00 | 6 premium models | Strategic decisions, technology selection, enterprise architecture |
| **`layered_consensus`** | Hierarchical | Variable | Tiered model selection | Comprehensive analysis building from junior through executive |
| **`quickreview`** | Basic Validation | $0.00 | 2-3 free models only | Syntax checking, quick validation, development testing |
| **`pr_prepare`** | Development Workflow | $0.00 | Git analysis only | PR preparation, branch validation, GitHub integration |
| **`pr_review`** | Adaptive Review | $0.00-25.00 | Adaptive scaling | GitHub PR review, quality gates, multi-agent coordination |

## When to Use Each Tool

### Basic Consensus (Junior Developer Level)
```
Use for: Development decisions, code reviews, basic feasibility checks
Budget: Intern/junior developer decision authority
Examples: "Should we use this library?", "Is this code structure okay?", "Basic security check needed"
```

### Review Consensus (Senior Staff Level)  
```
Use for: Production decisions, architecture reviews, professional analysis
Budget: Senior developer/team lead decision authority
Examples: "Should we migrate to microservices?", "Evaluate this new framework", "Production deployment decision"
```

### Critical Consensus (Executive Leadership Level)
```
Use for: Strategic decisions, enterprise architecture, technology investments
Budget: C-level/executive decision authority  
Examples: "Should we adopt this new technology stack?", "Enterprise security strategy", "Major system redesign"
```

### Layered Consensus (Hierarchical Analysis)
```
Use for: Comprehensive analysis requiring multiple organizational perspectives
Budget: Variable based on selected tier (junior/senior/executive)
Examples: "Get full organizational input on this proposal", "Need perspectives from all levels"
```

### QuickReview (Fast Validation)
```
Use for: Quick syntax checks, basic validation, development testing
Budget: Zero cost (free models only)
Examples: "Check this code for syntax errors", "Basic logic validation", "Quick feasibility check"
```

### PR Prepare (Development Workflow)
```
Use for: Pull request preparation, branch validation, GitHub integration
Budget: Zero cost (git analysis only, no AI models)
Examples: "Prepare comprehensive PR description", "Validate branch strategy", "Create draft PR with GitHub integration"
```

### PR Review (Adaptive Review)
```
Use for: GitHub PR review with adaptive analysis, quality gates, multi-agent coordination
Budget: Variable cost based on PR complexity ($0-25 adaptive scaling)
Examples: "Review PR for quality issues", "Security-focused PR analysis", "Performance optimization review"
```

## Model Selection Strategy

### Automatic Organizational Mapping

Each tool automatically selects appropriate models based on organizational level:

**Junior Developer Models:**
- Free tier models preferred (cost optimization)
- Basic capability requirements
- Focus on availability and reliability

**Senior Staff Models:**
- Professional-grade value tier models
- Balanced cost/performance optimization
- Enhanced reasoning and analysis capabilities

**Executive Leadership Models:**
- Premium tier models for strategic decisions
- Maximum capability and performance
- Comprehensive analysis and reasoning

### Role-Based Analysis

Each organizational level includes appropriate professional roles:

**Junior Level Roles:**
- Code Reviewer (basic quality checks)
- Security Checker (obvious vulnerabilities)
- Technical Validator (simple feasibility)

**Senior Level Roles:**
- Security Engineer (professional security analysis)
- Senior Developer (code quality and maintainability)
- System Architect (design patterns and scalability)
- DevOps Engineer (operational concerns)
- QA Engineer (testing strategies)

**Executive Level Roles:**
- Lead Architect (strategic system design)
- Technical Director (technology strategy)
- Security Chief (enterprise security)
- Research Lead (innovation opportunities)
- Risk Analysis Specialist (strategic risk)
- IT Director (operational alignment)

## Cost Management

### Budget-Appropriate Selection

The framework automatically selects models within appropriate budget ranges for each organizational level:

```
Junior Level:    $0.00 - $0.50   (Free models preferred, cheap paid fallback)
Senior Level:    $1.00 - $5.00   (Professional-grade value models)
Executive Level: $5.00 - $25.00  (Premium models for strategic decisions)
```

### Cost Transparency

All tools provide cost estimates and model selection transparency in their output, enabling informed decision-making about analysis depth and associated costs.

## Usage Patterns

### Progressive Decision Making

```bash
# Start with basic analysis for initial validation
zen basic_consensus "Should we implement feature X?"

# Escalate to senior level for production decisions  
zen review_consensus "Ready to deploy feature X to production?"

# Executive review for strategic implications
zen critical_consensus "Should feature X become our core platform strategy?"
```

### Comprehensive Analysis

```bash
# Get perspectives from all organizational levels
zen layered_consensus "Evaluate our proposed architecture migration" --org-level executive
```

### Development Workflow Integration

```bash
# Quick validation during development (free)
zen quickreview "Check this code for basic issues" --focus syntax

# PR preparation and GitHub integration (free)
zen pr_prepare --type feat --create-pr --target-branch phase-1-development

# Adaptive PR review with quality gates (variable cost)
zen pr_review --pr-url https://github.com/team/repo/pull/123 --mode adaptive

# Professional review before production (moderate cost)
zen review_consensus "Review this implementation for production readiness"
```

## Integration with Model Infrastructure

### Dynamic Model Selection

All consensus tools integrate with the `dynamic_model_selector` to:
- Automatically select optimal models for each organizational level
- Apply fallback strategies when preferred models are unavailable
- Maintain provider diversity and redundancy
- Optimize for cost-effectiveness within budget constraints

### Centralized Configuration

Model selection uses the centralized band system from `bands_config.json`:
- Organizational level bands determine model eligibility
- Cost tier bands ensure budget compliance
- Performance bands guarantee quality thresholds
- Role assignment bands map to appropriate professional roles

## Best Practices

### Choosing the Right Tool

1. **Match organizational authority**: Use the tool that matches the decision-maker's authority level
2. **Consider budget constraints**: Higher tiers cost more but provide deeper analysis
3. **Escalate appropriately**: Start with basic consensus and escalate to higher tiers as needed
4. **Use layered for comprehensive**: When you need input from multiple organizational levels

### Effective Usage

1. **Provide clear context**: Include project constraints, requirements, and background
2. **Specify focus areas**: Guide analysis toward relevant aspects (security, performance, cost)
3. **Include relevant files**: Provide code, documentation, or specifications for informed analysis
4. **Build on results**: Use continuation for follow-up analysis and refinement

### Cost Optimization

1. **Start with appropriate tier**: Don't over-analyze simple decisions with executive-level tools
2. **Use quickreview for development**: Free validation for syntax and basic logic checking
3. **Reserve critical consensus**: Use executive level only for strategic decisions
4. **Leverage layered consensus**: Get comprehensive coverage at optimized cost structure

## Technical Architecture

### Shared Infrastructure

All consensus tools inherit from `ConsensusToolBase` which provides:
- Model availability checking and fallback handling
- Standardized error handling and recovery
- Orchestrator model selection
- Result formatting and metadata enhancement

### Auto-Discovery System

Custom tools are automatically discovered and registered through:
- Plugin-style architecture in `/tools/custom/`
- Automatic tool registration without core file modifications
- Isolated development to minimize merge conflicts
- Dynamic loading and instantiation

### Integration Points

Custom tools integrate seamlessly with:
- **Zen MCP Server**: Standard tool registration and execution
- **Dynamic Model Selector**: Intelligent model routing and selection
- **Consensus Tool**: Core consensus analysis engine
- **Configuration System**: Centralized model and band configuration

This organizational framework enables realistic, budget-conscious decision-making that scales from individual development tasks to enterprise strategic decisions.