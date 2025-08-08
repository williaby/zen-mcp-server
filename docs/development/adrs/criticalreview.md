# CriticalReview Tool - Architecture Decision Record (ADR)

**Status**: 📋 PLANNED  
**Date**: 2025-08-08  
**Tool Name**: `criticalreview`  

## Overview
Executive-level critical decision analysis using 6+ premium models for high-stakes decisions.

## Purpose
- Major architectural decisions
- Root cause analysis for critical issues
- Comprehensive system design reviews
- Risk assessment and mitigation planning
- Strategic technology decisions
- Crisis response analysis

## Architecture Decisions

### Model Selection
- **Models**: All tiers including premium models
- **Count**: 6+ models for exhaustive analysis  
- **Cost**: Premium tier for critical decisions
- **Selection**: Best available models across all tiers

### Role-Based Analysis
Executive and senior expert roles:
- **Lead Architect**: Overall system design, long-term architectural vision
- **Technical Director**: Strategic technology decisions, cross-system impacts
- **Security Chief**: Comprehensive security analysis, risk assessment
- **Research Lead**: Cutting-edge approaches, innovation opportunities
- **System Integration Expert**: Inter-system dependencies, integration patterns
- **Risk Analysis Specialist**: Risk identification, mitigation strategies
- **Performance Expert**: Scalability analysis, performance implications
- **Operational Excellence**: Production readiness, operational concerns

### Workflow Design
- **Steps**: 7-step workflow (analysis → expert assignment → deep consultations → risk assessment → synthesis → recommendations → final validation)
- **Thinking**: High/Max thinking mode for comprehensive analysis
- **Temperature**: Varied by role (analytical for technical, creative for innovation)
- **Expert Analysis**: Always enabled for critical validation

## Implementation Plan

### Phase 1: Executive Framework
- [ ] Create tools/custom/criticalreview.py with premium model support
- [ ] Implement CriticalReviewRequest with executive-level fields
- [ ] Define premium + value + free model selection logic
- [ ] Create executive role assignment system

### Phase 2: Deep Analysis Workflow
- [ ] Implement 7-step comprehensive workflow
- [ ] Add deep consultation system with thinking modes
- [ ] Create risk assessment framework
- [ ] Build consensus with conflict resolution for executive decisions

### Phase 3: Validation & Reporting
- [ ] Add expert analysis validation layer
- [ ] Create comprehensive reporting format
- [ ] Implement cost tracking and approval workflow
- [ ] Add decision audit trail

## Key Features Planned
- Multi-tier model utilization (free + value + premium)
- Executive-level role specialization
- Deep thinking modes for complex analysis
- Risk assessment and mitigation planning
- Decision audit trail and documentation
- Cost awareness with approval thresholds
- Expert validation layer for critical decisions

## Usage (Planned)
```bash
criticalreview proposal:"Evaluate microservices migration strategy" files:["architecture/"] focus:"strategic" budget:"premium" approval_required:true
```

## Cost Analysis
- **Target**: $5.00-$20.00 per session (high-value decisions)
- **Models**: 6+ models across all tiers
- **Justification**: Critical decisions justify premium model costs
- **ROI**: High-value decisions require comprehensive analysis

## Dependencies
- [ ] Premium model identification and access
- [ ] Executive role prompt specialization
- [ ] Risk assessment framework
- [ ] Cost approval and tracking system
- [ ] Decision documentation templates
- [ ] Audit trail requirements

## Design Considerations
1. **Premium Model Access**: Ensure access to highest-tier models
2. **Cost Management**: Clear cost estimation and approval workflow
3. **Executive Roles**: Specialized prompts for senior-level analysis
4. **Deep Thinking**: Utilize maximum thinking capabilities
5. **Risk Focus**: Comprehensive risk identification and mitigation
6. **Decision Quality**: Optimize for highest quality analysis
7. **Audit Trail**: Full documentation for critical decision processes

## Success Criteria
- [ ] Access to premium models across providers
- [ ] Executive-level analysis quality
- [ ] Comprehensive risk assessment capability
- [ ] Clear cost/value justification
- [ ] Complete decision audit trail
- [ ] Integration with approval workflows
- [ ] Conflict resolution for high-stakes decisions

## Risk Considerations
- **Cost Control**: Premium models require budget oversight
- **Model Availability**: Premium models may have rate limits
- **Decision Authority**: Clear governance on who can approve critical reviews
- **Time Investment**: Deep analysis takes longer than basic reviews
- **Consensus Building**: Executive opinions may conflict more strongly

## Timeline
- **Start**: After review tool is complete and validated
- **Duration**: 2-3 development sessions (most complex)
- **Dependencies**: Premium model access validation, cost framework

## Integration Points
- Cost approval workflow
- Executive notification system
- Decision documentation system
- Risk management integration
- Audit trail preservation