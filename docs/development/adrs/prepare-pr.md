# Prepare PR - Development Checklist

**Status**: 📋 ACTIVE  
**Date**: 2025-08-08  

## Overview
Checklist for preparing PRs for the tiered consensus analysis system implementation.

## Current Status

### ✅ Completed Items
- [x] **Plugin Architecture**: Zero-conflict custom tools system implemented
- [x] **QuickReview Tool**: Complete implementation with optimized MCP interface  
- [x] **Auto-Discovery**: Automatic tool registration system
- [x] **Documentation**: Comprehensive custom-tools.md updates
- [x] **MCP Interface Optimization**: Reduced parameters from 19 to 12 (37% improvement)
- [x] **Testing Framework**: Self-contained test system
- [x] **ADR Documentation**: Restored architecture decision records

### 📋 Ready for PR Items

#### Core Implementation Files
- [x] `tools/custom/__init__.py` - Auto-discovery system (44 lines)
- [x] `tools/custom/quickreview.py` - Complete quickreview implementation (507 lines)
- [x] `tools/custom/test_quickreview.py` - Self-contained tests (77 lines)
- [x] `server.py` - Minimal integration (5 lines added)

#### Documentation Files  
- [x] `docs/custom-tools.md` - Comprehensive custom tools guide
- [x] `docs/development/adrs/quickreview.md` - QuickReview ADR with lessons learned
- [x] `docs/development/adrs/review.md` - Review tool architecture plan
- [x] `docs/development/adrs/criticalreview.md` - CriticalReview tool architecture plan
- [x] `docs/development/adrs/future.md` - Future enhancements roadmap
- [x] `docs/development/adrs/prepare-pr.md` - This checklist

## Pre-PR Validation Checklist

### Code Quality
- [ ] Run quality checks: `./code_quality_checks.sh`
- [ ] All linting passes (black, ruff, mypy)
- [ ] No syntax errors or warnings
- [ ] Code follows zen patterns and conventions

### Testing
- [ ] Self-contained test passes: `python tools/custom/test_quickreview.py`
- [ ] Server integration test: Custom tool loads in TOOLS
- [ ] MCP interface validation: Parameter count optimized
- [ ] No regression in existing tools

### Integration
- [ ] Server starts successfully with custom tools
- [ ] QuickReview tool appears in Claude Code MCP browser
- [ ] Tool parameters show optimized interface (12 vs 19)
- [ ] Auto-discovery system works correctly

### Documentation
- [ ] All ADR files complete and accurate
- [ ] custom-tools.md reflects current implementation
- [ ] Code comments are clear and helpful
- [ ] Usage examples are accurate

## PR Description Template

```markdown
# Add Plugin-Style Custom Tools Architecture with QuickReview Implementation

## Summary
Implements a zero-merge-conflict plugin architecture for custom tools and delivers the first tool: **QuickReview** for basic validation using free models.

## Key Features
- 🔌 **Plugin Architecture**: Zero-conflict custom tools in `tools/custom/`
- 🤖 **QuickReview Tool**: Basic validation with 2-3 free models ($0 cost)
- 📱 **MCP Interface**: Optimized from 19 to 12 parameters (37% reduction)
- 🔍 **Auto-Discovery**: Automatic tool registration with minimal core changes
- 📚 **Comprehensive Docs**: Complete implementation and design guides

## Implementation Details
- **Minimal Integration**: Only 5 lines added to `server.py`
- **Self-Contained**: All custom tools in isolated `tools/custom/` directory
- **Git-Independent**: No merge conflicts with upstream changes
- **Test Coverage**: Self-contained testing with validation framework

## Files Added/Modified
### New Files
- `tools/custom/__init__.py` - Auto-discovery system
- `tools/custom/quickreview.py` - QuickReview implementation  
- `tools/custom/test_quickreview.py` - Self-contained tests
- `docs/custom-tools.md` - Comprehensive custom tools guide
- `docs/development/adrs/*.md` - Architecture Decision Records

### Modified Files
- `server.py` - Added 5 lines for custom tool loading

## Testing
- ✅ Self-contained tests pass
- ✅ Server integration validated  
- ✅ MCP interface optimized
- ✅ Auto-discovery system working
- ✅ Zero merge conflicts confirmed

## Usage
```bash
quickreview proposal:"Check this code syntax" focus:"syntax" files:["src/auth.py"]
```

## Benefits
- **Zero Merge Conflicts**: Plugin architecture prevents upstream conflicts
- **Cost Effective**: Free models only for basic validation ($0 cost)
- **User Friendly**: Clean MCP interface with essential parameters
- **Extensible**: Foundation for tier 2 (review) and tier 3 (criticalreview) tools

## Next Steps  
- Implement **review** tool (tier 2) using same plugin architecture
- Add **criticalreview** tool (tier 3) for critical decisions
- Expand model selection and role-based analysis

Closes #[issue-number] if applicable
```

## Post-PR Actions

### Immediate (After Merge)
- [ ] Update project README if needed
- [ ] Notify team about new custom tools capability
- [ ] Start development of **review** tool (tier 2)

### Short Term (1-2 weeks)
- [ ] Gather user feedback on QuickReview tool
- [ ] Monitor model availability and performance
- [ ] Begin **review** tool implementation

### Medium Term (1-2 months)  
- [ ] Complete **review** and **criticalreview** tools
- [ ] Add advanced features based on user feedback
- [ ] Consider specialized domain tools (secreview, perfreview)

## Risk Mitigation

### Deployment Risks
- **Model Availability**: QuickReview includes robust fallback handling
- **Interface Changes**: MCP optimization maintains backward compatibility
- **Integration Issues**: Minimal server changes reduce risk

### Monitoring Points
- Custom tool auto-discovery functionality
- Free model availability and performance  
- User adoption of new tool
- MCP interface usability

## Success Criteria
- [ ] PR merged without conflicts
- [ ] QuickReview tool working in production
- [ ] No regression in existing functionality
- [ ] Users can successfully use QuickReview via MCP
- [ ] Foundation ready for tier 2 and 3 tools

---

**Developer Notes**: This PR establishes the foundation for the complete tiered consensus analysis system. The plugin architecture ensures all future custom tools can be developed without merge conflicts while maintaining full functionality and clean user interfaces.