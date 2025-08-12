# PR Prepare Tool - Comprehensive Pull Request Preparation

**Generate comprehensive PR descriptions with git analysis, branch validation, and GitHub integration**

The `pr_prepare` tool provides sophisticated pull request preparation capabilities including branch strategy validation, git history analysis, change impact assessment, PR template population, and GitHub integration with draft PR creation. Migrated from PromptCraft's workflow-prepare-pr slash command to zen custom tool architecture.

## Thinking Mode

**Not applicable.** PR Prepare uses direct execution without AI model consultation - performs comprehensive git analysis, content generation, and GitHub integration through deterministic processing.

## Model Recommendation

PR Prepare does not use AI models for analysis - it performs comprehensive git repository analysis, conventional commit parsing, change impact assessment, and GitHub integration through direct implementation.

## How It Works

PR Prepare provides comprehensive pull request preparation through systematic analysis:

1. **Branch strategy validation**: Validates current branch strategy with safety checks and user guidance
2. **Dependency validation**: Validates poetry.lock consistency and generates requirements files
3. **Git history analysis**: Analyzes commits with conventional commit parsing and issue detection
4. **Change impact assessment**: Calculates files, lines, complexity metrics and review tool compatibility
5. **PR content generation**: Creates structured PR descriptions from commit analysis and templates
6. **GitHub integration**: Optionally creates draft PRs with proper metadata, labels, and reviewers

## Example Prompts

**Basic PR Preparation:**
```
zen pr_prepare --target-branch main --type feat
```

**Phase Completion PR:**
```
zen pr_prepare --target-branch main --phase-merge --phase-number 1
```

**Security-Related PR:**
```
zen pr_prepare --type feat --security --create-pr --title "Add OAuth2 authentication"
```

**Breaking Change with Custom Options:**
```
zen pr_prepare --type feat --breaking --performance --create-pr --force-wtd
```

**Dry Run Validation:**
```
zen pr_prepare --dry-run --target-branch phase-1-development
```

## Key Features

- **Branch strategy validation**: Prevents accidental commits to main, validates phase targeting
- **Automatic safety checks**: Detects improper branch usage and guides corrective actions
- **Dependency management**: Validates poetry.lock and regenerates requirements files automatically
- **Comprehensive git analysis**: Parses conventional commits, detects issues, analyzes change patterns
- **Review tool compatibility**: Checks GitHub Copilot, WhatTheDiff, and optimal size limits
- **PR size analysis**: Classifies PR size and provides splitting suggestions for large changes
- **GitHub integration**: Creates draft PRs with automatic push, labels, and reviewer suggestions
- **Intelligent content generation**: Auto-generates titles, summaries, and structured descriptions
- **WhatTheDiff integration**: Smart WTD shortcode handling based on PR size and flags

## Tool Parameters

**Core Parameters:**
- `target_branch`: Target branch for the PR (default: "main")
- `base_branch`: Base branch for comparison (default: "auto")
- `change_type`: Type of change - feat, fix, docs, style, refactor, perf, test, chore (default: "feat")

**Content Customization:**
- `title`: Custom PR title (default: "auto" - generate from commits)
- `issue_number`: Related issue number
- `phase_number`: Phase number for phase-based development

**Flags for Special Handling:**
- `breaking`: Contains breaking changes (default: false)
- `security`: Contains security-related changes (default: false)
- `performance`: Contains performance impacts (default: false)
- `phase_merge`: Phase completion PR targeting main (default: false)

**GitHub Integration:**
- `create_pr`: Create draft PR on GitHub (default: false)
- `no_push`: Skip automatic push to GitHub (default: false)

**Content Options:**
- `include_wtd`: Include WhatTheDiff summary shortcode (default: true)
- `force_wtd`: Force WTD inclusion even for large PRs (default: false)

**Advanced Options:**
- `skip_deps`: Skip dependency validation and requirements generation (default: false)
- `force_target`: Override branch validation safety checks (default: false)
- `dry_run`: Run validation only, don't create PR (default: false)

## Branch Strategy Validation

### Safety Checks

**Main Branch Protection:**
- Prevents creating PRs from main branch
- Detects when working on main and provides guidance
- Ensures proper feature branch usage

**Phase Targeting Validation:**
- Validates targeting main from non-phase branches
- Provides branch strategy recommendations
- Guides users toward proper phase branch usage

**Issue Detection:**
- Analyzes commits for issue references
- Suggests proper branch naming conventions
- Provides automatic branch migration assistance

### Branch Validation Process

```bash
# Example validation flow
Current branch: feature-auth-implementation
Target branch: main
Base branch: main

⚠️ WARNING: Targeting main branch from non-phase branch!
🤔 This looks like it should target a phase branch instead of main.

Phase Strategy Recommendations:
- Use issue-specific branches for feature work
- Target phase-development branches
- Reserve main for phase completion PRs
```

## Dependency Management

### Poetry.lock Validation

**Consistency Checking:**
- Validates poetry.lock against pyproject.toml changes
- Detects dependency conflicts before PR creation
- Automatically regenerates lock file when needed

**Requirements Generation:**
- Runs scripts/generate_requirements.sh automatically
- Updates requirements.txt, requirements-dev.txt, requirements-docker.txt
- Ensures Docker build consistency with poetry.lock
- Commits requirements updates with proper conventional commit message

### Security Validation

**Dependency Security:**
- Runs safety check for known vulnerabilities
- Reports critical and high-severity issues
- Provides security assessment in PR preparation

## Git Analysis Features

### Conventional Commit Parsing

**Commit Type Detection:**
- Supports standard conventional commit types (feat, fix, docs, etc.)
- Detects breaking changes (BREAKING CHANGE, !)
- Extracts scopes and descriptions
- Groups commits by type and scope

**Issue Reference Extraction:**
- Finds issue references (#123, closes #456)
- Detects related issues for proper branch targeting
- Connects commits to phase-specific work

**Co-Author Detection:**
- Identifies AI co-authors (Claude, Copilot)
- Formats proper co-author attribution
- Maintains contribution history

### Change Impact Assessment

**File Statistics:**
- Total files added, modified, removed
- Language breakdown from file extensions
- Test file vs source file ratio
- Configuration and documentation changes

**Size Metrics:**
- Total lines added/removed
- PR size classification (Small < 100, Medium < 400, Large < 1000, XL > 1000)
- Token estimation for review tools
- Complexity scoring

**Review Tool Compatibility:**
- GitHub Copilot: Max 28 files
- WhatTheDiff: Max 2500 tokens  
- Optimal review size: < 400 lines
- Warning thresholds and recommendations

## PR Content Generation

### Automatic Title Generation

**From Conventional Commits:**
- Uses primary commit type for emoji selection
- Extracts description from first commit
- Includes scope when available
- Formats: "✨ feat(auth): Add OAuth2 authentication"

**Emoji Mapping:**
- feat: ✨, fix: 🐛, docs: 📚, style: 💎
- refactor: ♻️, perf: ⚡, test: ✅, chore: 🔧
- security: 🔒, breaking: 💥, phase-completion: 🎯

### Structured Description Generation

**Content Sections:**
- Change summary with metrics table
- Summary from commit analysis
- WhatTheDiff integration (conditional)
- Detailed change breakdown
- Size warnings and splitting suggestions
- Review checklist and testing instructions

**Metrics Table:**
```markdown
| Metric | Value | Status |
|--------|-------|--------|
| **Files Changed** | 15 | ✅ Medium |
| **Total Lines** | +250 / -45 | ✅ |
| **Commits** | 8 | ✅ |
| **Copilot Compatible** | 15/28 files | ✅ |
| **Base Branch** | `main` | ✅ |
```

### Size Analysis and Warnings

**PR Size Classifications:**
- Small: < 100 lines, < 10 files
- Medium: 100-400 lines, 10-20 files  
- Large: 400-1000 lines, 20-50 files
- XL: > 1000 lines, > 50 files

**Review Tool Compatibility Table:**
```markdown
| Tool | Current | Limit | Status |
|------|---------|-------|--------|
| **GitHub Copilot** | 25 files | 28 files | ✅ Compatible |
| **WhatTheDiff** | ~1800 tokens | 2500 tokens | ✅ Compatible |
| **Review Size** | 350 lines | 400 lines | ✅ Optimal |
```

**Splitting Suggestions:**
- Provides concrete splitting strategies for large PRs
- Suggests organization by functionality, tests, and configuration
- Includes git commands for implementing splits

## GitHub Integration

### Automatic Push and PR Creation

**Push Strategy:**
- Pushes current branch to origin with upstream tracking
- Handles existing branches gracefully
- Validates GitHub CLI authentication

**Draft PR Creation:**
- Creates draft PR with generated title and description
- Sets appropriate base and head branches
- Applies automatic labels based on change analysis

### Label Generation

**Automatic Labels:**
- Change type (feat, fix, docs, etc.)
- Size classification (size/small, size/medium, etc.)
- Special flags (breaking-change, security, performance)
- Phase labels (phase-1, phase-completion)

**Example Label Set:**
```
feat, size/medium, security, phase-1
```

### Reviewer Assignment

**CODEOWNERS Integration:**
- Reads .github/CODEOWNERS for suggested reviewers
- Assigns reviewers based on changed files
- Supports team and individual assignments

## WhatTheDiff Integration

### Intelligent Shortcode Handling

**Inclusion Logic:**
```python
if args.force_wtd:
    include_wtd = True
elif args.no_wtd:
    include_wtd = False  
elif pr_description_length > 10000:
    include_wtd = False  # Auto-exclude for large PRs
else:
    include_wtd = True   # Default inclusion
```

**Shortcode Placement:**
- Placed after summary section when included
- Clean formatting on separate line
- Respects size limits to prevent overwhelming descriptions

## Usage Examples

### Development Workflow Example

```bash
# 1. Feature development on issue branch
git checkout -b issue-23-user-authentication

# 2. Make changes and commit with conventional format
git commit -m "feat(auth): implement OAuth2 login flow

- Add OAuth2 client configuration
- Implement login/logout endpoints  
- Add user session management
- Include security middleware

Closes #23"

# 3. Prepare PR with validation and GitHub creation
zen pr_prepare --type feat --security --create-pr --issue-number 23

# 4. Tool performs comprehensive analysis:
# ✅ Branch strategy validation
# ✅ Dependency validation  
# ✅ Git history analysis
# ✅ Change impact assessment
# ✅ PR content generation
# ✅ GitHub integration

# 5. Result: Draft PR created with comprehensive description
```

### Phase Completion Example

```bash
# Phase completion PR from phase branch to main
git checkout phase-1-development

zen pr_prepare --target-branch main --phase-merge --phase-number 1 --create-pr

# Creates phase completion PR with:
# - Phase-specific metrics and summary
# - Comprehensive issue completion tracking
# - Version release information
# - Phase acceptance criteria checklist
```

### Large PR with Splitting Suggestions

```bash
zen pr_prepare --type refactor --target-branch main

# Output includes size warnings:
# ⚠️ PR Size Warning
# This PR exceeds recommended size limits for optimal review
# 
# Suggested PR Split Plan:
# 1. Core refactoring (Priority: High) - 12 files, 250 lines
# 2. Test updates (Priority: Medium) - 8 files, 180 lines  
# 3. Documentation (Priority: Low) - 5 files, 120 lines
```

## Error Handling and Recovery

### Git Repository Validation

**Repository Checks:**
- Validates git repository presence
- Ensures working on named branch (not detached HEAD)
- Checks remote connectivity for GitHub operations

**Error Recovery:**
- Clear error messages with corrective actions
- Guidance for common git issues
- Helpful suggestions for repository setup

### GitHub Integration Failures

**Authentication Issues:**
- Checks GitHub CLI installation and authentication
- Provides clear setup instructions
- Graceful fallback when GitHub operations fail

**Network and API Issues:**
- Handles GitHub API rate limits
- Provides retry suggestions
- Maintains local PR content for manual creation

## Best Practices

- **Use conventional commits**: Enables proper commit parsing and categorization
- **Follow branch strategy**: Use feature branches and proper targeting
- **Review generated content**: Always review auto-generated PR descriptions
- **Test before creating**: Use --dry-run flag to validate without creating PRs
- **Maintain dependencies**: Keep poetry.lock consistent with pyproject.toml
- **Security awareness**: Flag security-related changes for proper review
- **Size management**: Keep PRs within optimal size limits for better reviews

## Integration with Development Workflow

### Pre-PR Checklist

```bash
# 1. Validate branch strategy
zen pr_prepare --dry-run

# 2. Run code quality checks  
./code_quality_checks.sh

# 3. Validate dependencies
poetry check --lock

# 4. Create comprehensive PR
zen pr_prepare --create-pr --type feat
```

### CI/CD Integration

```yaml
# Example GitHub Actions integration
- name: Validate PR preparation
  run: |
    zen pr_prepare --dry-run --target-branch ${{ github.base_ref }}
    
- name: Auto-create draft PR
  if: startsWith(github.ref, 'refs/heads/feature/')
  run: |
    zen pr_prepare --create-pr --type feat --target-branch phase-1-development
```

## Advanced Configuration

### Custom PR Templates

The tool uses intelligent template population but can be customized through:

**Template Variables:**
- ${pr_emoji}, ${pr_title}, ${phase_number}, ${issue_reference}
- ${files_changed}, ${lines_added}, ${lines_removed}, ${pr_size_label}
- ${pr_summary}, ${pr_motivation}, ${changes_added}, ${usage_example}

**Size Limit Customization:**
```python
PR_SIZE_LIMITS = {
    "small": {"lines": 100, "files": 10},
    "medium": {"lines": 400, "files": 20}, 
    "large": {"lines": 1000, "files": 50}
}
```

### Review Tool Integration

**GitHub Copilot**: Automatically checks 28-file limit
**WhatTheDiff**: Token estimation and 2500-token limit checking
**Manual Review**: Optimal 400-line recommendations with warnings

## Technical Implementation Details

### Architecture Integration

**BaseTool Implementation:**
- Extends BaseTool for zen framework integration
- Uses Pydantic models for request validation
- Implements comprehensive error handling

**Git Integration:**
- Direct subprocess calls for git operations
- Robust error handling and validation
- Support for complex git workflows

**GitHub CLI Integration:**
- Uses gh CLI for authenticated GitHub operations
- Handles authentication and permissions
- Provides fallback options for manual operations

This comprehensive PR preparation tool brings the sophisticated functionality of PromptCraft's workflow-prepare-pr slash command into the zen framework, providing developers with enterprise-grade PR preparation capabilities including safety checks, dependency management, and GitHub integration.