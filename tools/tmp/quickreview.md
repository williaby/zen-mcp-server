# QuickReview Tool - Architecture Decision Record (ADR)

**Status**: ✅ IMPLEMENTED  
**Date**: 2025-08-08  
**Tool Name**: `quickreview`  

## Overview
Basic validation tool using 2-3 free models only for zero-cost validation tasks.

## Purpose
- Grammar and syntax checking
- Basic code validation  
- Documentation review
- Simple logic verification

## Architecture Decisions

### Model Selection
- **Models**: Free tier models only (cost = $0)
- **Count**: 2-3 models maximum for speed
- **Priority**: deepseek-r1-distill-llama-70b:free, llama-3.1-405b:free, qwen-2.5-coder-32b:free
- **Fallback**: Dynamic availability checking with robust error handling

### Role-Based Analysis
- **syntax_checker**: Grammar, formatting, obvious errors
- **logic_reviewer**: Basic logic flow and consistency  
- **docs_checker**: Documentation clarity and completeness

### Workflow Design
- **Steps**: 3-step workflow (analysis → consultation → synthesis)
- **Thinking**: Low thinking mode for speed
- **Temperature**: Analytical temperature (0.2) for consistency
- **Expert Analysis**: None (self-contained for speed)

## Implementation Status
- ✅ **Core Implementation**: tools/custom/quickreview.py (507 lines)
- ✅ **Auto-Discovery**: tools/custom/__init__.py (44 lines)
- ✅ **Self-Contained Tests**: tools/custom/test_quickreview.py (77 lines)
- ✅ **Plugin Architecture**: Zero merge conflicts
- ✅ **MCP Interface**: Optimized from 19 to 12 parameters (37% reduction)
- ✅ **Server Integration**: Minimal (5 lines in server.py)

## Key Features Implemented
- Dynamic free model selection with availability fallback
- Role-based analysis assignment
- Embedded system prompt (no external files needed)
- Self-contained workflow execution
- Clean MCP interface with excluded internal fields
- Robust error handling for model outages

## Usage
```bash
quickreview proposal:"Check this code syntax" files:["src/auth.py"] focus:"syntax"
```

## Cost Analysis
- **Per session**: $0.00 (free models only)
- **Models**: 2-3 free tier models
- **Speed**: Optimized for fast validation

## Lessons Learned
1. **MCP Interface**: Base WorkflowRequest exposes too many parameters (19) - need custom schema
2. **Model Availability**: Free models have outages - need robust fallback handling
3. **Plugin Architecture**: Zero-conflict approach works perfectly for custom tools
4. **User Experience**: 12 parameters much more manageable than 19 for MCP interface

## Next Steps
- ✅ Completed and ready for use
- 📋 Use lessons learned for **review** tool (tier 2) implementation
- 📋 Apply plugin architecture pattern to remaining tools