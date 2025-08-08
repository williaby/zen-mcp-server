# Review Tool - Architecture Decision Record (ADR)

**Status**: 📋 PLANNED  
**Date**: 2025-08-08  
**Tool Name**: `review`  

## Overview
Peer review panel using 5-7 value tier models with IT governance role-based analysis.

## Purpose
- Development team reviews
- Pull request analysis
- Code troubleshooting
- Architecture discussions
- Process validation

## Architecture Decisions

### Model Selection
- **Models**: Value tier models (≤$10 output/M tokens)
- **Count**: 5-7 models for comprehensive coverage
- **Cost Target**: Moderate cost for balanced analysis
- **Selection**: Dynamic from current_models.md value tier

### Role-Based Analysis
IT governance roles for comprehensive review:
- **Security Engineer**: Security implications, vulnerability assessment
- **Senior Developer**: Code quality, best practices, maintainability
- **System Architect**: Design patterns, scalability, architecture decisions
- **DevOps Engineer**: Deployment, infrastructure, operational concerns
- **QA Engineer**: Testing strategy, edge cases, quality assurance
- **Technical Lead**: Overall coordination, final synthesis
- **Performance Engineer**: Performance implications, optimization opportunities

### Workflow Design
- **Steps**: 5-step workflow (analysis → role assignment → consultations → synthesis → recommendations)
- **Thinking**: Medium thinking mode for balanced analysis
- **Temperature**: Analytical temperature for consistent feedback
- **Expert Analysis**: Optional for complex issues

## Implementation Plan

### Phase 1: Core Structure
- [ ] Create tools/custom/review.py using quickreview pattern
- [ ] Implement ReviewRequest with tier 2 specific fields
- [ ] Define value tier model selection logic
- [ ] Create role assignment system for IT governance

### Phase 2: Workflow Implementation
- [ ] Implement 5-step workflow execution
- [ ] Add role-based consultation system
- [ ] Create synthesis logic for multiple expert opinions
- [ ] Add consensus building for conflicting recommendations

### Phase 3: Testing & Interface
- [ ] Create tools/custom/test_review.py
- [ ] Optimize MCP interface (target: 10-12 parameters)
- [ ] Add simulator test integration
- [ ] Validate with real-world scenarios

## Key Features Planned
- Dynamic value tier model selection
- IT governance role-based analysis
- Consensus building for conflicting opinions
- Cost tracking and budget awareness
- Clean MCP interface with essential parameters only
- Comprehensive test coverage

## Usage (Planned)
```bash
review proposal:"Review this authentication system" files:["src/auth/"] focus:"security" budget:"moderate"
```

## Cost Analysis
- **Target**: $0.50-$2.00 per session
- **Models**: 5-7 value tier models
- **Roles**: IT governance specialization
- **ROI**: Balanced cost/value for team reviews

## Dependencies
- [ ] Value tier model identification from current_models.md
- [ ] Role prompt templates for IT governance
- [ ] Cost tracking integration
- [ ] Consensus algorithm for conflicting opinions

## Design Considerations
1. **Plugin Architecture**: Use same zero-conflict approach as quickreview
2. **MCP Interface**: Learn from quickreview optimization (target 10-12 params)
3. **Model Availability**: Include fallback handling for value tier outages
4. **Role Specialization**: Each role should have specific expertise prompts
5. **Consensus Building**: Handle disagreements between different roles
6. **Cost Awareness**: Track and report estimated costs before execution

## Success Criteria
- [ ] Comprehensive IT governance role coverage
- [ ] Balanced cost/value proposition
- [ ] Clean, usable MCP interface
- [ ] Robust model availability handling
- [ ] Effective consensus building
- [ ] Integration with existing workflow patterns

## Timeline
- **Start**: After quickreview lessons are documented
- **Duration**: 1-2 development sessions
- **Dependencies**: Plugin architecture validation complete