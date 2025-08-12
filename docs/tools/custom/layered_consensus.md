# Layered Consensus Tool - Hierarchical Organizational Analysis

**Get comprehensive consensus across organizational hierarchy using cost-efficient layered model selection**

The `layered_consensus` tool implements a realistic organizational hierarchy approach where higher tiers build upon lower-tier analysis, creating a cost-effective method for comprehensive decision-making that mirrors real IT organizational structures.

## Thinking Mode

**Not applicable.** Layered consensus uses predetermined organizational models and hierarchical roles - the underlying consensus analysis handles any required reasoning at the model level.

## Model Recommendation

Layered consensus automatically selects from a tiered model approach based on the specified organizational level, optimizing cost by using appropriate models for each role level while building comprehensive analysis through organizational hierarchy.

## How It Works

Layered consensus provides hierarchical organizational analysis through an incremental approach:

1. **Layered model selection**: Automatically builds model selection from junior through specified tier
2. **Incremental role assignment**: Assigns appropriate roles for each organizational level
3. **Cost-efficient escalation**: Higher tiers include all lower-tier analysis for comprehensive coverage
4. **Hierarchical consensus orchestration**: Uses the core consensus engine with layered parameters
5. **Organizational transparency**: Shows complete organizational breakdown with cost optimization

## Organizational Structure

### Junior Level (3 models)
- **Models**: 3 free models for cost optimization
- **Roles**: Basic analysis roles (Code Reviewer, Security Checker, Technical Validator)
- **Cost**: $0.00-0.50 (free models preferred)
- **Authority**: Entry-level development decisions

### Senior Level (6 models)
- **Models**: 3 junior + 3 professional value models
- **Roles**: Basic + professional analysis roles (+ Security Engineer, Senior Developer, System Architect)
- **Cost**: $1.00-5.00 (junior costs + professional models)
- **Authority**: Production decisions and architecture reviews

### Executive Level (8 models)
- **Models**: 3 junior + 3 senior + 2 premium models
- **Roles**: Basic + professional + strategic roles (+ Lead Architect, Technical Director)
- **Cost**: $5.00-25.00 (junior + senior costs + premium models)
- **Authority**: Strategic decisions and enterprise architecture

## Example Prompts

**Junior Level Analysis:**
```
zen layered_consensus "Should we use React or Vue for our new component library?" --org-level junior
```

**Senior Level Analysis:**
```
zen layered_consensus "Should we migrate our monolith to microservices?" --org-level senior
```

**Executive Level Analysis:**
```
zen layered_consensus "Should we adopt a cloud-native architecture strategy?" --org-level executive
```

**Default Senior Analysis:**
```
zen layered_consensus "Evaluate this new framework for production use"
```

## Key Features

- **Cost-efficient layering**: Higher tiers include lower-tier analysis without duplicate costs
- **Organizational realism**: Mirrors actual IT hierarchy structures and decision-making patterns
- **Comprehensive coverage**: Ensures all organizational perspectives are included in higher-tier analysis
- **Flexible tier selection**: Choose appropriate organizational level based on decision importance
- **Transparent cost structure**: Clear breakdown of costs across organizational levels
- **Incremental complexity**: Simple decisions can use junior level, complex decisions get full hierarchy
- **Real-world modeling**: Reflects how actual organizations make technology decisions
- **Budget optimization**: Maximizes analysis depth while controlling costs through appropriate tier selection

## Tool Parameters

**Required:**
- `proposal`: The question or proposal to analyze via layered consensus (required)

**Optional:**
- `org_level`: Organizational level - "junior", "senior", or "executive" (defaults to "senior")

**Automatic Configuration:**
- Models: Layered selection based on organizational level
- Roles: Hierarchical roles assigned automatically for each tier
- Cost: Optimized cost structure based on organizational tier selection

## Organizational Level Details

### Junior Level (org_level: "junior")

**Model Strategy:**
- 3 free models for zero-cost basic analysis
- Focus on availability and basic technical competency
- Cost optimization through free model priority

**Role Coverage:**
- Code Reviewer: Basic code quality and syntax checking
- Security Checker: Obvious security issues and common vulnerabilities
- Technical Validator: Basic technical feasibility and logic validation

**Decision Scope:**
- Development decisions and code reviews
- Basic feasibility checks and MVP choices
- Entry-level technical validation
- Frequent decision support without budget concerns

### Senior Level (org_level: "senior")

**Model Strategy:**
- 3 junior-level free models + 3 professional value models
- Balanced cost/performance for production decisions
- Professional-grade analysis within reasonable budget

**Role Coverage:**
- **Junior Tier**: Code Reviewer, Security Checker, Technical Validator
- **Professional Tier**: Security Engineer, Senior Developer, System Architect, DevOps Engineer, QA Engineer

**Decision Scope:**
- Production decisions and architecture reviews
- Technology evaluation and framework selection
- System design and scalability planning
- Professional-level technical analysis

### Executive Level (org_level: "executive")

**Model Strategy:**
- 3 junior-level + 3 senior-level + 2 premium executive models
- Maximum capability for strategic decisions
- Comprehensive analysis across all organizational levels

**Role Coverage:**
- **Junior Tier**: Code Reviewer, Security Checker, Technical Validator
- **Professional Tier**: Security Engineer, Senior Developer, System Architect, DevOps Engineer, QA Engineer
- **Executive Tier**: Lead Architect, Technical Director, Security Chief, Research Lead, Risk Analysis Specialist, IT Director

**Decision Scope:**
- Strategic decisions and enterprise architecture
- Major technology investments and migrations
- Crisis response and business continuity planning
- C-level and board-level decision support

## Usage Examples

**Development Framework Decision (Junior Level):**
```
zen layered_consensus "Should we adopt TypeScript for our JavaScript project?" --org-level junior

# Expected layered analysis:
# Junior Level (3 free models):
# - Code Reviewer: Evaluates code quality and maintainability benefits
# - Security Checker: Considers type safety security implications  
# - Technical Validator: Assesses learning curve and development impact
```

**Production Migration Decision (Senior Level):**
```
zen layered_consensus "Should we migrate from MySQL to PostgreSQL?" --org-level senior

# Expected layered analysis:
# Junior Level (3 models): Basic feasibility and implementation concerns
# + Professional Level (3 models): Production impact and professional assessment
# Total: 6 models across junior + professional tiers
```

**Enterprise Strategy Decision (Executive Level):**
```
zen layered_consensus "Should we adopt a cloud-native microservices architecture?" --org-level executive

# Expected layered analysis:
# Junior Level (3 models): Implementation and development considerations
# + Professional Level (3 models): Production, security, and operational analysis
# + Executive Level (2 models): Strategic vision and enterprise-wide impact
# Total: 8 models across all organizational tiers
```

**Technology Evaluation (Default Senior):**
```
zen layered_consensus "Should we implement GraphQL for our API architecture?"

# Defaults to senior level - gets junior + professional perspectives
# Balanced analysis appropriate for most production decisions
```

## Cost and Budget Management

### Layered Cost Structure

Layered consensus optimizes costs through incremental tier building:

**Junior Level Cost ($0.00-0.50):**
- 3 free models for basic analysis
- Zero or minimal cost for frequent decisions
- Entry-level budget appropriate for development choices

**Senior Level Cost ($1.00-5.00):**
- Junior costs + 3 professional value models
- Professional-grade analysis within reasonable budget
- Cost-effective for production decisions

**Executive Level Cost ($5.00-25.00):**
- Junior + Senior costs + 2 premium models
- Strategic analysis for enterprise decisions
- Maximum capability when decisions matter most

### Cost Transparency Example

```
LAYERED CONSENSUS COMPLETE

Organizational Approach: Layered Senior Level Analysis
Total Models: 6 models across organizational tiers
Model Breakdown: ~3 junior + ~3 senior models (basic + professional)
Estimated Cost: $3.50
Architecture: Cost-efficient layered approach (basic → professional → strategic)
Tool: layered_consensus

TIER BREAKDOWN:
Junior Tier (Free): deepseek/deepseek-r1-distill-llama-70b:free, meta-llama/llama-3.1-405b-instruct:free, qwen/qwen-2.5-coder-32b-instruct:free
Professional Tier (Value): anthropic/claude-sonnet-4, openai/gpt-5-mini, google/gemini-2.5-flash
```

## Best Practices

- **Match decision importance**: Use junior for development, senior for production, executive for strategy
- **Optimize for frequent use**: Junior level enables regular decision support without budget concerns
- **Escalate appropriately**: Start with lower tiers and escalate to higher tiers for complex decisions
- **Consider time sensitivity**: Higher tiers provide more comprehensive analysis but may take longer
- **Budget planning**: Use layered approach to control costs while ensuring appropriate analysis depth
- **Organizational alignment**: Choose tier that matches the actual decision-maker's authority level
- **Progressive analysis**: Use results from lower tiers to inform whether higher-tier analysis is needed

## Integration with Development Workflows

### Progressive Decision Making

```bash
# Start with junior level for initial validation
zen layered_consensus "Is this approach technically feasible?" --org-level junior

# Escalate to senior level for production readiness
zen layered_consensus "Is this ready for production deployment?" --org-level senior

# Executive level for strategic implications
zen layered_consensus "Should this become our standard approach?" --org-level executive
```

### Workflow Integration

```yaml
# Example CI/CD integration
- name: Development decision validation
  run: |
    zen layered_consensus "Should we proceed with this code change?" \
      --org-level junior --files changed_files.txt

- name: Production deployment gate
  run: |
    zen layered_consensus "Is this change ready for production?" \
      --org-level senior --files deployment_plan.md
```

### Budget-Conscious Development

```bash
# Free analysis for frequent development decisions
zen layered_consensus "Should we refactor this component?" --org-level junior

# Professional analysis for architecture decisions
zen layered_consensus "Should we adopt this new architecture pattern?" --org-level senior
```

## Error Handling and Fallbacks

**Model Availability Issues:**
- Automatic fallback through model priority lists for each tier
- Graceful degradation while maintaining organizational structure
- Clear messaging when fallback models are used

**Insufficient Models:**
- Minimum model requirements validation for each tier
- Helpful error messages with tier requirement details
- Suggestion to retry with lower tier if insufficient models available

**Cost Budget Overruns:**
- Transparent cost estimation before execution
- Warning messages about budget implications
- Option to select lower tier for budget-conscious analysis

## When to Use Layered Consensus vs Other Tools

- **Use `layered_consensus`** for: Comprehensive analysis requiring multiple organizational perspectives, budget-conscious comprehensive coverage
- **Use `basic_consensus`** for: Simple development decisions, cost-optimized analysis, junior-level authority
- **Use `review_consensus`** for: Professional production decisions, senior staff authority level
- **Use `critical_consensus`** for: Strategic decisions, maximum capability analysis, executive authority
- **Use `quickreview`** for: Quick validation without comprehensive organizational analysis

## Organizational Hierarchy Benefits

### Realistic Decision Modeling

Layered consensus mirrors real organizational structures:

**Bottom-Up Perspective:**
- Junior level identifies implementation concerns and practical challenges
- Professional level adds production experience and operational considerations
- Executive level provides strategic vision and enterprise-wide impact assessment

**Comprehensive Coverage:**
- Technical feasibility (junior perspective)
- Production readiness (professional perspective)  
- Strategic alignment (executive perspective)
- Risk assessment across all organizational levels

### Cost-Effective Escalation

**Smart Resource Allocation:**
- Use appropriate model costs for each organizational level
- Avoid over-analyzing simple decisions with expensive models
- Ensure comprehensive coverage for important decisions through layered approach

**Budget Optimization:**
- Junior decisions use free models for zero cost
- Professional decisions add value models for balanced cost/capability
- Strategic decisions include premium models for maximum insight

## Technical Architecture

### Layered Model Selection

The tool uses the dynamic model selector's layered approach:

```python
# Example layered selection for senior level
layered_models = {
    "junior": ["free_model_1", "free_model_2", "free_model_3"],
    "professional": ["value_model_1", "value_model_2", "value_model_3"]
}
```

### Role Assignment Strategy

Each tier gets appropriate roles for their organizational level:

**Junior Roles**: Basic technical validation and obvious issue identification
**Professional Roles**: Production concerns, security analysis, architectural considerations  
**Executive Roles**: Strategic vision, innovation opportunities, enterprise risk assessment

### Integration Points

Layered consensus integrates seamlessly with:
- **Dynamic Model Selector**: Intelligent layered model routing and selection
- **Consensus Tool**: Core consensus analysis engine with layered parameters
- **Configuration System**: Centralized model and organizational band configuration
- **Cost Management**: Transparent cost tracking across organizational tiers

This layered approach provides realistic, cost-effective decision-making that scales from individual development tasks to enterprise strategic decisions while maintaining organizational structure and budget consciousness.