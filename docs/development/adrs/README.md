# Custom Tools Development Directory

**⚠️ IMPORTANT: DO NOT DELETE THIS DIRECTORY ⚠️**

This directory contains critical Architecture Decision Records (ADRs) for custom tool development.

## Purpose
This directory serves as the development workspace and documentation hub for custom tools development, specifically the tiered consensus analysis system.

## Contents

### Architecture Decision Records (ADRs)
- **`quickreview.md`** - ✅ IMPLEMENTED - Basic validation tool using free models
- **`review.md`** - 📋 PLANNED - Peer review tool using value tier models  
- **`criticalreview.md`** - 📋 PLANNED - Executive analysis using premium models
- **`future.md`** - 🔮 FUTURE - Long-term enhancements and extensions
- **`prepare-pr.md`** - 📋 ACTIVE - PR preparation checklist and validation

### Protection Files
- **`.gitkeep`** - Ensures directory is preserved in git
- **`README.md`** - This file - explains directory purpose and protection

## Directory Protection Strategy

### 1. Git Tracking
- All `.md` files are tracked in git
- `.gitkeep` ensures directory persists even if empty
- Regular commits preserve development history

### 2. Documentation References
- `docs/custom-tools.md` references these ADR files
- CLAUDE.md mentions this directory in development workflow
- README files link to this documentation

### 3. Explicit Warnings
- Clear "DO NOT DELETE" warnings in multiple files
- Explanation of contents and importance
- References from other parts of the codebase

## Safe Cleanup Guidelines

### What CAN be deleted:
- Temporary test files (`.tmp`, `.test` extensions)
- Build artifacts or generated files
- Personal notes or scratch files

### What MUST NOT be deleted:
- Any `.md` files (ADRs and documentation)
- `.gitkeep` file
- `README.md` (this file)
- The directory itself

### Before any cleanup:
1. Read file contents to understand purpose
2. Check if file is referenced elsewhere in codebase
3. Verify it's not an ADR or important documentation
4. When in doubt, don't delete

## Recovery Process

If this directory is accidentally deleted:

1. **Check git history**: `git log --follow docs/development/adrs/`
2. **Restore from git**: `git checkout HEAD~1 -- docs/development/adrs/`
3. **Recreate from conversation**: ADR contents are in Claude conversation history
4. **Validate completeness**: Ensure all 5 ADR files are restored

## Integration Points

This directory is referenced by:
- `docs/custom-tools.md` - Custom tool registry
- Development workflow documentation
- Future custom tool implementations
- PR preparation processes

## Development Workflow

When working on custom tools:
1. **Review existing ADRs** for architectural decisions
2. **Update ADRs** as implementations progress  
3. **Add new ADRs** for additional custom tools
4. **Reference ADRs** in implementation files
5. **Preserve directory** through all cleanup operations

---

**Remember**: These ADRs represent significant architectural work and planning. Losing them means losing institutional knowledge and development decisions that guide the custom tools system.