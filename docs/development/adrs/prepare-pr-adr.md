# Prepare-PR Tool - Architecture Decision Record (ADR)

**Status**: 📋 PLANNED  
**Date**: 2025-08-08  
**Tool Name**: `prepare-pr`

## Overview
AI-enhanced pull request preparation with intelligent branch strategy analysis and automated GitHub integration.

## Purpose
- Complex PR workflow automation
- Phase-aware development support  
- Intelligent change analysis
- Automated documentation generation
- GitHub integration optimization

## Source Command Reference
**Original Implementation**: `/home/byron/dev/PromptCraft/.claude/commands/workflow-prepare-pr.md`  
**Complexity**: 955 lines of sophisticated bash scripting  
**Key Features**: Branch validation, phase-aware workflows, dependency management, GitHub integration, What The Diff integration

## Architecture Decisions

### ADR-001: Base Class Selection
**Decision**: Inherit from `WorkflowTool`  
**Rationale**: 
- Complex multi-step workflow with systematic progression required
- Branch strategy analysis needs investigative phases with AI reasoning
- PR description generation benefits from conversation memory and context building
- Integration with zen's conversation threading for complex analysis
- Enables detailed investigation and synthesis across multiple workflow steps

### ADR-002: Migration Strategy - Why Convert This Command
**Decision**: Convert the 955-line workflow-prepare-pr bash command to MCP tool
**Rationale**:
- **Complexity Justification**: 955 lines of bash with complex business logic becomes unmaintainable
- **AI Enhancement Value**: Intelligent branch strategy recommendations vs rigid rule-based validation
- **Context Benefits**: Conversation memory allows building context across git history, change analysis, and PR generation
- **Error Handling**: Sophisticated error recovery and user guidance vs basic bash error handling
- **Testing**: Full integration testing framework vs limited bash testing capabilities
- **Maintainability**: Python class structure vs increasingly complex bash script maintenance

### ADR-003: AI Integration Points - Where AI Adds Value Over Bash Rules
**Decision**: Leverage AI for intelligent analysis, keep deterministic operations as structured logic  

**AI-Enhanced Features**:
- **Branch Strategy Analysis**: Analyze change patterns, commit history, and project context to suggest optimal branching
- **PR Description Generation**: Generate contextual, comprehensive PR descriptions from commit analysis and change patterns
- **Change Impact Assessment**: Intelligent risk assessment and reviewer suggestions based on change complexity
- **Conflict Resolution**: Smart suggestions for branch strategy conflicts and workflow optimizations
- **Reviewer Assignment**: Analyze change patterns and suggest appropriate reviewers based on expertise areas

**Deterministic Operations** (keep as structured logic):
- Git command execution and status checking
- File system operations and validation
- API calls to GitHub
- Template variable substitution
- Cost tracking and budget management

### ADR-004: Branch Strategy Analysis - Intelligent vs Rule-Based
**Decision**: Hybrid approach with AI-enhanced decision support  

**Implementation Approach**:
```python
def analyze_branch_strategy(self, git_context, change_patterns, commit_history):
    # Deterministic rule validation first
    basic_validation = self.validate_basic_branch_rules(git_context)
    
    if basic_validation.has_conflicts:
        # AI reasoning for complex conflict resolution
        ai_analysis = self.get_ai_branch_strategy_recommendation(
            context=git_context,
            patterns=change_patterns,
            history=commit_history,
            conflicts=basic_validation.conflicts
        )
        return self.synthesize_branch_recommendation(basic_validation, ai_analysis)
    
    return basic_validation
```

**Rationale**: 
- Maintains fast, deterministic validation for clear-cut cases
- Leverages AI reasoning for complex scenarios requiring judgment
- Provides intelligent guidance while preserving rule-based safety

### ADR-005: PR Description Generation - Template-Based vs AI-Generated
**Decision**: AI-generated content with template structure and variable population  

**Implementation**:
```python
def generate_pr_description(self, analysis_context):
    # Use AI to generate content for each template section
    sections = {
        "summary": self.ai_generate_pr_summary(analysis_context),
        "changes": self.ai_analyze_change_impact(analysis_context), 
        "testing": self.ai_generate_testing_guidance(analysis_context),
        "architecture": self.ai_assess_architectural_impact(analysis_context)
    }
    
    # Populate structured template with AI-generated content
    return self.populate_pr_template(sections, analysis_context.metadata)
```

**Rationale**:
- AI generates contextual, comprehensive content vs static templates
- Maintains structured format for consistency and tool compatibility
- Reduces manual PR description effort while improving quality
- Leverages git history and change analysis for better descriptions

### ADR-006: Model Selection Strategy - Role-Based Analysis
**Decision**: Use plugin-style architecture with specialized model assignment for different workflow aspects  

**Model Assignments**:
```python
WORKFLOW_MODEL_ROLES = {
    "branch_analysis": {
        "models": ["o3-mini", "gemini-2.5-flash"],
        "focus": "logical reasoning, rule analysis, decision trees"
    },
    "change_impact": {
        "models": ["deepseek-r1", "qwen3-coder"], 
        "focus": "code analysis, architectural impact, technical assessment"
    },
    "pr_description": {
        "models": ["gemini-2.5-pro", "o3"],
        "focus": "comprehensive writing, context synthesis, documentation"
    },
    "reviewer_assignment": {
        "models": ["o3-mini", "gemini-2.5-flash"],
        "focus": "pattern recognition, team dynamics, expertise matching"
    }
}
```

**Cost Management**:
- Target value tier models (≤$10 output/M) for cost effectiveness
- Dynamic model selection based on current availability and pricing
- Budget controls with intelligent fallback strategies
- Detailed cost tracking per workflow phase

### ADR-007: Architecture Approach - Plugin-Style Implementation
**Decision**: Use plugin-style architecture following the new custom-tools approach

**Implementation Structure**:
- **Location**: `tools/custom/prepare_pr.py`
- **Auto-Discovery**: Automatic registration via plugin system
- **Zero Conflicts**: No core file modifications required
- **Self-Contained**: Embedded system prompts and test files
- **MCP Interface**: Custom `get_input_schema()` for clean user interface

**Benefits**:
- Zero merge conflicts with upstream updates
- Automatic tool discovery and registration
- Self-contained implementation with embedded prompts
- Clean MCP interface optimized for usability

## Implementation Plan

### Phase 1: Core Structure (Week 1)
- [ ] Create tools/custom/prepare_pr.py using plugin pattern
- [ ] Implement PrepPRRequest with workflow-specific fields
- [ ] Define git context analysis and branch validation logic
- [ ] Create basic workflow structure with 6-step process

### Phase 2: AI Enhancement Integration (Week 2)
- [ ] Implement AI-powered branch strategy analysis
- [ ] Add intelligent PR description generation
- [ ] Create change impact assessment with AI reasoning
- [ ] Add conflict resolution and recommendation systems

### Phase 3: GitHub Integration (Week 3)
- [ ] Implement GitHub CLI integration for repository operations
- [ ] Add automated PR creation and management
- [ ] Create intelligent reviewer assignment system
- [ ] Add What The Diff integration logic

### Phase 4: Testing & Interface (Week 4)
- [ ] Create tools/custom/test_prepare_pr.py
- [ ] Optimize MCP interface (target: 12-15 parameters)
- [ ] Add comprehensive simulator test integration
- [ ] Validate with complex workflow scenarios

## Technical Specifications

### Workflow Structure
**Decision**: 6-step workflow with AI-enhanced analysis phases  
1. **Step 1**: Repository analysis and git context gathering
2. **Step 2**: Branch strategy analysis with AI-enhanced recommendations  
3. **Step 3**: Change impact assessment and dependency validation
4. **Step 4**: PR content generation with AI-powered description creation
5. **Step 5**: GitHub integration and reviewer assignment
6. **Step 6**: Final validation and reporting

### Complex Logic Decomposition

**Branch Validation and Safety Logic** (Source: lines 18-313):
- Comprehensive branch strategy validation with phase-aware logic
- Intelligent conflict detection and resolution recommendations
- User confirmation flows for complex scenarios
- Automated branch reorganization with safety checks

**Phase-Aware Workflow Management** (Source: lines 488-685):
- Integration with phase-based development methodology
- Intelligent phase completion vs feature work detection
- Context-aware branch targeting recommendations
- Phase relationship analysis and documentation

**Dependency Validation and Requirements Generation** (Source: lines 316-476):
- Poetry.lock consistency validation and repair
- Automated requirements.txt generation with security hashes
- Dependency conflict detection and resolution suggestions
- Security vulnerability scanning with intelligent risk assessment

**PR Template Population and Variable Substitution** (Source: lines 574-641):
- AI-generated content for template sections
- Context-aware variable population from git analysis
- Intelligent change categorization and impact assessment
- Automated testing instruction generation

**GitHub Integration and Draft PR Creation** (Source: lines 756-883):
- Automated branch pushing with error handling
- Draft PR creation with comprehensive metadata
- Intelligent label assignment based on change analysis
- Reviewer suggestion based on change patterns and expertise

**What The Diff Integration Logic** (Source: lines 709-740):
- Character limit detection and intelligent shortcode inclusion
- Context-aware WTD summary optimization
- User preference handling with override capabilities

## MCP Interface Design

### Parameter Optimization
Following the plugin architecture best practices for clean user interface:

**Essential Parameters** (show to users):
- `description`: What changes to prepare PR for
- `target_branch`: Target branch (auto-detect if not specified)
- `change_type`: Change type (feat, fix, docs - auto-detect from commits)
- `create_pr`: Create draft PR automatically (default: true)
- `budget_limit`: Optional cost cap in dollars
- `tier`: Budget tier (basic, standard, premium)

**Hide from MCP Interface**:
- Internal workflow state (`files_checked`, `relevant_context`, `issues_found`)
- Advanced workflow control (`hypothesis`, `backtrack_from_step`, `confidence`)
- Technical parameters (`use_assistant_model`, `use_websearch`)
- Complex configuration details

**Target**: 12-15 parameters for manageable complex tool interface

## Key Features Planned

### AI-Enhanced Analysis
- Intelligent branch strategy recommendations based on change patterns
- Context-aware PR description generation using commit analysis
- Smart change impact analysis and risk assessment
- Automated conflict resolution suggestions for branch strategies
- Intelligent reviewer assignment based on change patterns and history

### GitHub Workflow Integration
- Automated repository analysis and git context gathering
- Phase-aware branch validation and strategy recommendations
- Dependency management with poetry/requirements integration
- Draft PR creation with comprehensive metadata
- What The Diff integration with intelligent optimization

### Cost Management
- Dynamic model selection based on current availability and pricing
- Budget controls with intelligent fallback strategies
- Real-time cost tracking during multi-step analysis
- Detailed cost reporting per workflow phase
- Tiered service levels (basic, standard, premium)

## Testing Strategy

### Self-Contained Testing
```python
# tools/custom/test_prepare_pr.py
def test_prepare_pr_workflow():
    """Test prepare-pr tool with comprehensive workflow"""
    response = call_tool("prepare_pr", {
        "description": "Implement new authentication system with JWT tokens",
        "files": ["auth.py", "models.py", "tests/test_auth.py"],
        "change_type": "feat",
        "security": True,
        "budget_limit": 3.00,
        "tier": "standard"
    })
    
    # Verify workflow completion
    assert_workflow_completed(response)
    assert_branch_strategy_analyzed(response)
    assert_pr_description_generated(response)
    assert_budget_respected(response, 3.00)
    assert_github_integration_completed(response)
```

### Test Scenarios
- **Basic PR Creation**: Simple feature branch to development
- **Complex Branch Strategy**: Phase completion with multiple conflicts
- **Security Changes**: Security-focused analysis and reviewer assignment
- **Large PR Handling**: Change impact analysis and splitting suggestions
- **Cost Management**: Budget limit enforcement and model fallback
- **Error Recovery**: Git conflicts, GitHub API failures, model unavailability

## Usage (Planned)
```bash
prepare-pr description:"Implement JWT authentication system" change_type:"feat" security:true budget_limit:3.00
```

## Cost Analysis
- **Target**: $1.00-$5.00 per session depending on complexity
- **Models**: Value tier models (≤$10 output/M)
- **Workflow**: 6-step analysis with role-based model assignment
- **ROI**: Significant time savings vs manual PR preparation

## Dependencies
- [ ] Value tier model identification from current_models.md
- [ ] Git context analysis and repository integration
- [ ] GitHub CLI integration for repository operations
- [ ] Poetry/pip integration for dependency management
- [ ] Conversation memory system for workflow state
- [ ] Cost tracking and budget management system

## Success Criteria
- [ ] Successfully converts 955-line bash complexity to maintainable Python workflow
- [ ] Provides intelligent branch strategy recommendations superior to rule-based validation
- [ ] Generates comprehensive, contextual PR descriptions automatically
- [ ] Maintains cost effectiveness with value tier model usage
- [ ] Integrates seamlessly with GitHub workflow automation
- [ ] Handles edge cases and errors gracefully with user guidance
- [ ] Demonstrates clear AI reasoning value over original bash implementation
- [ ] Clean MCP interface with 12-15 user-friendly parameters
- [ ] Zero merge conflicts using plugin architecture

## Risk Assessment

### Technical Risks
- **Model Dependency**: Reliance on external AI providers for core functionality
- **Cost Management**: Potential for unexpected high usage costs with complex workflows
- **Complexity**: Significant increase in implementation and maintenance complexity vs bash
- **Performance**: Potential latency increase vs immediate bash execution

### Mitigation Strategies
- **Model Fallback**: Graceful degradation to simpler analysis if models unavailable
- **Cost Controls**: Hard budget limits with intelligent optimization and user warnings
- **Plugin Architecture**: Zero-conflict implementation reduces maintenance overhead
- **Performance Optimization**: Efficient workflow design and intelligent caching strategies

### Success Dependencies
- **AI Value Demonstration**: Clear benefits over bash implementation must be evident
- **Cost Effectiveness**: Usage costs must remain reasonable for regular development use
- **Reliability**: Must handle edge cases and errors better than original 955-line implementation
- **User Adoption**: Must improve workflow efficiency to justify increased complexity

## Timeline
- **Phase 1**: 1 week - Core structure and basic workflow
- **Phase 2**: 1 week - AI enhancement integration  
- **Phase 3**: 1 week - GitHub integration and automation
- **Phase 4**: 1 week - Testing, interface optimization, and validation
- **Total**: 4 weeks for complete implementation and testing

## Future Enhancements
- Integration with CI/CD pipeline analysis for deployment impact assessment
- Advanced security analysis with automated vulnerability detection
- Performance impact prediction based on change analysis
- Cross-repository change analysis for microservice architectures
- Integration with project management tools for automatic issue linking
- Custom organization role definitions and reviewer assignment logic

---

*This ADR captures the architectural decisions for converting the 955-line workflow-prepare-pr bash command into a sophisticated AI-enhanced WorkflowTool using the plugin architecture approach for zero-conflict upstream compatibility.*