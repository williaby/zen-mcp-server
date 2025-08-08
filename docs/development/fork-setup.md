# Fork Setup Guide for Zen MCP Server Custom Tools

## Overview
This guide walks through setting up a GitHub fork to safely develop custom tools while staying synchronized with upstream updates.

## Benefits of Fork Approach
- ✅ **Version control** for custom tools and ADRs
- ✅ **Remote backup** - never lose your work
- ✅ **Structured upstream updates** with conflict resolution
- ✅ **Future collaboration** capability 
- ✅ **Contribution pathway** to upstream if desired
- ✅ **Professional workflow** using standard Git patterns

## Step-by-Step Setup

### 1. Create GitHub Fork
1. Go to the original zen-mcp-server repository on GitHub
2. Click "Fork" button (top right)
3. Choose your account as the destination
4. Keep the same repository name
5. ✅ Check "Copy the main branch only" for cleaner start

### 2. Update Local Repository
```bash
# Add your fork as new origin
git remote rename origin upstream  # Rename original to upstream
git remote add origin https://github.com/YOUR_USERNAME/zen-mcp-server.git

# Verify remotes
git remote -v
# Should show:
# origin    https://github.com/YOUR_USERNAME/zen-mcp-server.git (fetch)
# origin    https://github.com/YOUR_USERNAME/zen-mcp-server.git (push)  
# upstream  https://github.com/ORIGINAL_OWNER/zen-mcp-server.git (fetch)
# upstream  https://github.com/ORIGINAL_OWNER/zen-mcp-server.git (push)
```

### 3. Push Current Work to Fork
```bash
# Push current branch to your fork
git push -u origin main

# Push custom tools and ADRs (override protection for this initial push)
git add -f tools/custom/ docs/development/adrs/ docs/custom-tools.md
git add backup_adrs.sh restore_adrs.sh CLAUDE.md
git commit --no-verify -m "Add custom tools plugin architecture with QuickReview

- Plugin-style architecture with zero merge conflicts  
- QuickReview tool for basic validation using free models
- Comprehensive ADR documentation and development guides
- Local backup and recovery system
- MCP interface optimization (19→12 parameters)
"
git push origin main
```

## Ongoing Workflow

### Daily Development
```bash
# Work on custom tools normally
vim docs/development/adrs/review.md
vim tools/custom/review.py
./backup_adrs.sh  # Still create local backups as safety net

# Commit custom work to your fork
git add tools/custom/ docs/development/adrs/
git commit -m "Implement review tool (tier 2)"
git push origin main
```

### Sync with Upstream (Weekly/Monthly)
```bash
# Fetch latest upstream changes
git fetch upstream

# Check what's new upstream  
git log HEAD..upstream/main --oneline

# Merge upstream changes
git checkout main
git merge upstream/main

# If conflicts occur, resolve them and commit
# Your plugin architecture should minimize conflicts

# Push updated main to your fork
git push origin main
```

### Handle Merge Conflicts (If They Occur)
```bash
# If merge conflicts happen:
git status  # See conflicted files

# Edit conflicted files, resolve conflicts
vim server.py  # Example: merge your 5 lines with upstream changes

# Mark resolved and commit
git add server.py
git commit -m "Merge upstream changes, preserve custom tools integration"
git push origin main
```

## Branch Strategy Options

### Option A: Direct Main Development (Simplest)
- Develop custom tools directly on main branch
- Merge upstream updates into main
- Pro: Simple workflow
- Con: Main branch has both custom and upstream changes

### Option B: Custom Tools Branch (Recommended)
```bash
# Create dedicated branch for custom tools
git checkout -b custom-tools
git push -u origin custom-tools

# Develop custom tools on this branch
# Periodically merge main (with upstream updates) into custom-tools
git checkout main
git merge upstream/main
git push origin main

git checkout custom-tools  
git merge main  # Bring upstream updates to custom tools branch
git push origin custom-tools
```

### Option C: Feature Branches (Most Professional)
```bash
# Create feature branch for each tool
git checkout -b feature/review-tool
# Develop review tool
git commit -m "Implement review tool"
git push origin feature/review-tool

# Create PR within your own fork to merge to main
# This gives you review history and clean main branch
```

## Advantages Over Local-Only

### Version Control Benefits
- **Full history** of custom tool development
- **Remote backup** - survives local disasters
- **Branch management** for different features
- **Collaboration ready** if team grows

### Upstream Integration Benefits  
- **Structured updates** using standard Git workflows
- **Conflict resolution** with proper tools and history
- **Rollback capability** if upstream update breaks something
- **Contribution pathway** to upstream via PRs

### Professional Benefits
- **Portfolio showcase** - your custom tools are visible
- **Learning Git workflows** - valuable skill development
- **Open source participation** - standard practices
- **Documentation** - fork serves as documentation of your work

## Risk Mitigation

### Backup Strategy
- **Primary**: Your GitHub fork (remote backup)
- **Secondary**: Local backups with backup_adrs.sh (unchanged)
- **Tertiary**: Fork can be cloned anywhere for additional backups

### Merge Conflict Prevention
- **Plugin architecture**: Minimal core file changes reduce conflicts
- **Regular syncing**: Stay close to upstream to avoid large conflicts
- **Clear separation**: Custom code in dedicated directories

### Upstream Update Safety
```bash
# Test upstream updates safely
git checkout -b test-upstream-merge
git merge upstream/main
# Test everything works
./code_quality_checks.sh
python communication_simulator_test.py --quick

# If good, apply to main
git checkout main
git merge test-upstream-merge
git push origin main
```

## Migration from Current Setup

### 1. Preserve Current Protection System
- Keep .git/info/exclude for any future local-only work
- Keep backup scripts as additional safety net  
- Keep pre-commit hooks to prevent accidental staging

### 2. Gradual Migration
- Start with fork setup but keep local protections
- Test upstream merge process
- Gradually rely more on fork, less on local-only
- Remove local protections once comfortable with fork workflow

## Conclusion

The fork approach provides:
- ✅ **Better upstream integration** than local-only
- ✅ **Professional workflow** with version control
- ✅ **Future flexibility** for collaboration and contribution  
- ✅ **Robust backup** strategy with remote storage
- ✅ **Learning opportunity** for important Git skills

Your plugin architecture makes this transition smooth with minimal merge conflicts.