# PR Review Tool - Adaptive GitHub PR Review with Intelligent Scaling

**Sophisticated GitHub PR review with adaptive analysis, quality gates, and multi-agent coordination**

The `pr_review` tool provides adaptive PR review capabilities that scale from 2-minute quick reviews to 45-minute comprehensive analysis based on PR complexity. Features quality gate validation, multi-agent coordination, GitHub integration, and actionable feedback with copy-paste fix commands. Migrated from PromptCraft's workflow-pr-review slash command to zen custom tool architecture.

## Thinking Mode

**Not applicable.** PR Review uses direct execution with optional AI model consultation through multi-agent coordination - performs GitHub data fetching, quality analysis, and report generation through deterministic processing with intelligent scaling.

## Model Recommendation

PR Review automatically selects appropriate analysis depth based on PR complexity, with optional AI model consultation for complex cases requiring security, performance, or architectural analysis through the zen consensus system.

## How It Works

PR Review provides adaptive analysis through intelligent scaling:

1. **Smart PR analysis**: Fetches PR data from GitHub with fallback strategies and determines analysis strategy
2. **Quality gate validation**: Runs progressive quality checks with early exit for clear rejection cases
3. **Adaptive scaling**: Scales analysis complexity based on PR size, content, and quality issues found
4. **Multi-agent coordination**: Coordinates specialized agents for security, performance, and architectural analysis
5. **Smart consensus**: Generates consensus decisions using appropriate approach (direct/lightweight/comprehensive)
6. **Actionable reporting**: Creates detailed reports with copy-paste fix commands and GitHub integration

## Example Prompts

**Adaptive Review (Default):**
```
zen pr_review --pr-url https://github.com/owner/repo/pull/123
```

**Quick Review (Essential Checks Only):**
```
zen pr_review --pr-url https://github.com/owner/repo/pull/124 --mode quick
```

**Security-Focused Review:**
```
zen pr_review --pr-url https://github.com/owner/repo/pull/125 --mode security-focus
```

**Thorough Review with GitHub Submission:**
```
zen pr_review --pr-url https://github.com/owner/repo/pull/126 --mode thorough --submit-review --review-action request_changes
```

**Performance-Focused Review:**
```
zen pr_review --pr-url https://github.com/owner/repo/pull/127 --mode performance-focus --force-multi-agent
```

## Key Features

- **Adaptive analysis**: Automatically scales from 2-45 minute analysis based on PR complexity and quality issues
- **Early exit optimization**: Provides immediate feedback for clear rejection cases (>10 quality issues)
- **Quality gate validation**: Progressive quality checks including CI/CD, linting, security, and performance
- **Multi-agent coordination**: Coordinates specialized agents for security, performance, and architectural analysis
- **Large PR handling**: Intelligent sampling strategy for PRs >20K lines or >50 files
- **Smart consensus**: Chooses appropriate consensus approach (direct/lightweight/comprehensive)
- **GitHub integration**: Fetches PR data and optionally submits reviews with proper formatting
- **Actionable feedback**: Generates copy-paste fix commands and specific improvement guidance
- **Error resilience**: Graceful fallbacks for GitHub API issues and model availability

## Tool Parameters

**Core Parameters:**
- `pr_url`: GitHub PR URL to review (required)
- `mode`: Review mode - "adaptive", "quick", "thorough", "security-focus", "performance-focus" (default: "adaptive")

**Analysis Options:**
- `focus_security`: Enable additional security analysis (default: false)
- `focus_performance`: Enable performance optimization analysis (default: false)
- `skip_quality_gates`: Skip automated quality checks (default: false)
- `force_multi_agent`: Force multi-agent analysis even for simple cases (default: false)

**Output Options:**
- `submit_review`: Submit review to GitHub (draft by default) (default: false)
- `review_action`: GitHub review action - "approve", "request_changes", "comment" (default: "comment")
- `include_fix_commands`: Include copy-paste fix commands (default: true)

**Advanced Options:**
- `max_files_analyzed`: Maximum number of files to analyze (default: 50)
- `use_sampling`: Force sampling strategy for large PRs (default: false)
- `consensus_model`: Consensus model selection - "auto", "lightweight", "comprehensive" (default: "auto")

## Review Modes

### Adaptive Mode (Default)
**Intelligence**: Automatically scales based on PR complexity and content
**Time Range**: 5-45 minutes
**Early Exit**: Enabled for clear cases
**Use Case**: Default mode for most PR reviews - balances thoroughness with efficiency

**Scaling Logic:**
- Small PRs (<500 lines, <5 files): Quick analysis (5-10 minutes)
- Medium PRs (500-2K lines, 5-15 files): Standard analysis (10-20 minutes)
- Large PRs (2K-10K lines, 15-35 files): Comprehensive analysis (20-35 minutes)
- XL PRs (>10K lines, >35 files): Sampling strategy with focused analysis (25-45 minutes)

### Quick Mode
**Intelligence**: Essential review only with quality gates and basic analysis
**Time Range**: 2-10 minutes
**Early Exit**: Enabled for efficiency
**Use Case**: Small PRs, obvious issues, time-constrained reviews

**Focus Areas:**
- CI/CD status validation
- Basic linting and quality checks
- Security pattern detection
- Immediate actionable feedback

### Thorough Mode
**Intelligence**: Full multi-agent analysis regardless of complexity
**Time Range**: 15-45 minutes
**Early Exit**: Disabled - always performs complete analysis
**Use Case**: Critical PRs, complex changes, architectural modifications

**Analysis Depth:**
- Complete quality gate validation
- Multi-agent coordination for all aspects
- Comprehensive consensus analysis
- Detailed architectural and design review

### Security-Focus Mode
**Intelligence**: Enhanced security analysis with specialized agents
**Time Range**: 10-30 minutes
**Early Exit**: Disabled for security thoroughness
**Use Case**: Authentication changes, security features, vulnerability fixes

**Security Analysis:**
- Authentication and authorization patterns
- Input validation and sanitization
- Cryptographic implementations
- Dependency security scanning
- Security configuration review

### Performance-Focus Mode
**Intelligence**: Performance optimization analysis with specialized agents
**Time Range**: 10-30 minutes
**Early Exit**: Disabled for performance thoroughness
**Use Case**: Algorithm changes, database optimizations, performance improvements

**Performance Analysis:**
- Algorithm complexity analysis
- Resource usage patterns
- Database query optimization
- Caching strategy evaluation
- Performance bottleneck identification

## Quality Gate System

### Progressive Quality Checks

**Phase 1: CI/CD Status (Fastest)**
- GitHub Actions/CI status
- Build and test results
- Deployment pipeline status
- Critical failure detection

**Phase 2: File-Type Linting**
- Python: Ruff linting with fix commands
- Markdown: Markdownlint validation
- YAML: Yamllint configuration checking
- File-specific quality standards

**Phase 3: Security Scanning (Conditional)**
- Security pattern detection
- Dependency vulnerability checks
- Authentication/authorization review
- Configuration security validation

**Phase 4: Performance Checks (Conditional)**
- Algorithm complexity analysis
- Resource usage patterns
- Performance regression detection
- Optimization opportunity identification

### Early Exit Logic

**Trigger Conditions:**
- Quality issues > 10: Immediate feedback with fix commands
- CI/CD failures + multiple linting issues: Direct rejection with guidance
- Critical security vulnerabilities: Security-focused review required

**Benefits:**
- Saves 15-40 minutes for clear rejection cases
- Provides immediate actionable feedback
- Reduces unnecessary analysis overhead
- Maintains review quality for complex cases

## Adaptive Analysis Strategy

### Small PRs (< 500 lines, < 5 files)
**Strategy**: Quick validation with lightweight consensus
**Time**: 5-10 minutes
**Analysis**: Quality gates + basic review
**Consensus**: Direct or lightweight

### Medium PRs (500-2K lines, 5-15 files)
**Strategy**: Standard analysis with selective multi-agent
**Time**: 10-20 minutes
**Analysis**: Full quality gates + targeted agent coordination
**Consensus**: Lightweight or comprehensive based on issues

### Large PRs (2K-10K lines, 15-35 files)
**Strategy**: Comprehensive analysis with multi-agent coordination
**Time**: 20-35 minutes
**Analysis**: Complete quality gates + multi-agent analysis
**Consensus**: Comprehensive with specialized agents

### XL PRs (> 10K lines, > 35 files)
**Strategy**: Sampling with focused analysis on core changes
**Time**: 25-45 minutes
**Analysis**: Core file sampling + comprehensive multi-agent
**Consensus**: Comprehensive with splitting recommendations

## Multi-Agent Coordination

### Agent Selection Logic

**Security Agent** (Conditional):
- Triggered by: security-focus mode, auth/encrypt/token patterns
- Analysis: Authentication, authorization, input validation, crypto
- Model: High-capability models for security analysis

**Performance Agent** (Conditional):
- Triggered by: performance-focus mode, optimize/cache/database patterns
- Analysis: Algorithm complexity, resource usage, bottlenecks
- Model: Technical analysis models for performance evaluation

**Edge Case Agent** (Complex PRs):
- Triggered by: Quality issues > 3, thorough mode, complex changes
- Analysis: Edge cases, error handling, boundary conditions
- Model: Comprehensive models for architectural analysis

**Test Architect Agent** (Complex PRs):
- Triggered by: Missing tests, complex logic, architectural changes
- Analysis: Test coverage, test strategy, quality assurance
- Model: Testing-focused models for QA analysis

### Model Validation and Fallbacks

**Availability Testing:**
- Tests each model before use with simple validation call
- Graceful degradation when preferred models unavailable
- Fallback to alternative models maintaining analysis quality

**Priority Models:**
- High-capability: claude-opus-4, o3, anthropic/claude-sonnet-4
- Value models: o4-mini, deepseek/deepseek-chat-v3-0324
- Free fallbacks: deepseek/deepseek-r1-distill-llama-70b:free

## Smart Consensus System

### Consensus Mode Selection

**Direct Consensus:**
- Triggered by: >10 quality issues, clear rejection cases
- Process: Immediate actionable feedback without multi-agent
- Time: 2-5 minutes
- Output: Direct recommendations with fix commands

**Lightweight Consensus:**
- Triggered by: ≤3 quality issues, simple PRs, quick mode
- Process: Single high-quality model assessment
- Time: 5-15 minutes
- Output: Focused recommendations with basic multi-perspective

**Comprehensive Consensus:**
- Triggered by: Complex PRs, multiple agents needed, thorough mode
- Process: Full multi-agent analysis with consensus synthesis
- Time: 15-45 minutes
- Output: Detailed analysis with comprehensive recommendations

### Consensus Quality Assurance

**Model Diversity**: Uses different model families for balanced perspective
**Role Specialization**: Assigns specific expertise roles to each model
**Synthesis Process**: Combines insights while avoiding redundancy
**Confidence Scoring**: Provides confidence levels based on consensus agreement

## GitHub Integration

### PR Data Fetching

**Primary Method: GitHub CLI**
```bash
gh pr view [number] --json title,author,baseRefName,headRefName,state,url,body,files,additions,deletions,commits
```

**Fallback Method: GitHub API**
- Direct API calls when CLI unavailable
- Authentication handling with personal access tokens
- Rate limiting and error handling

**Error Resilience:**
- Multiple fallback strategies for data fetching
- Graceful degradation for partial data availability
- Clear error messages with manual analysis options

### Review Submission

**Draft Review Creation:**
- Creates GitHub review in draft status by default
- Populates review body with generated report
- Applies appropriate review action (approve/request_changes/comment)

**Review Metadata:**
- Adds review labels based on analysis results
- Links to specific issues and recommendations
- Includes analysis metadata (time, agents used, consensus mode)

## Report Generation

### Structured Report Format

**Quick Summary Section:**
- Recommendation (APPROVE/REQUEST_CHANGES/COMMENT)
- Confidence level (High/Medium/Low)
- Analysis time and consensus mode

**PR Overview Section:**
- Author, CI/CD status, branch information
- Impact metrics (files changed, lines added/removed)
- PR size classification

**Quality Gate Results:**
- CI/CD status with specific failure details
- Code quality violations with counts
- Security and performance scan results
- Test coverage analysis (when available)

**Analysis Summary:**
- Detailed findings from quality gates
- Multi-agent analysis results (when performed)
- Security and performance assessments
- Architectural and design considerations

**Required Actions:**
- Immediate blockers with specific fix commands
- Recommended improvements with priority levels
- Copy-paste fix commands for efficient resolution

### Copy-Paste Fix Commands

**Automated Command Generation:**
```bash
# Example generated commands
poetry run ruff check --fix src/auth/
markdownlint --fix docs/README.md
yamllint --config .yamllint.yml config/
gh pr checks [PR_NUMBER]
```

**Command Benefits:**
- Eliminates manual command construction
- Ensures correct syntax and parameters
- Provides verification commands for validation
- Reduces developer friction for fix implementation

## Usage Examples

### Development Workflow Integration

**Daily PR Review Process:**
```bash
# 1. Quick validation of small changes
zen pr_review --pr-url https://github.com/team/repo/pull/101 --mode quick

# 2. Standard review for feature additions
zen pr_review --pr-url https://github.com/team/repo/pull/102 --mode adaptive

# 3. Security review for auth changes
zen pr_review --pr-url https://github.com/team/repo/pull/103 --mode security-focus --submit-review

# 4. Performance review for optimization work
zen pr_review --pr-url https://github.com/team/repo/pull/104 --mode performance-focus --force-multi-agent
```

### Large PR Handling Example

```bash
# XL PR with sampling strategy
zen pr_review --pr-url https://github.com/team/repo/pull/105 --mode adaptive --use-sampling

# Output shows:
# 🔍 Large PR detected (25,000 lines, 75 files) - using sampling strategy
# ⚡ Analyzing core files (10 selected from 75 total)
# 🤖 Coordinating 3 specialized agents: security, performance, edge-case
# 📝 Generating comprehensive report with splitting recommendations
```

### Security-Focused Review Example

```bash
zen pr_review --pr-url https://github.com/team/repo/pull/106 --mode security-focus --focus-security

# Expected analysis includes:
# 🔒 Security Agent: Authentication pattern analysis
# 🛡️ Input validation and sanitization review
# 🔐 Cryptographic implementation evaluation
# 🚨 Dependency vulnerability scanning
# 📋 Security configuration assessment
```

### CI/CD Integration

```yaml
# GitHub Actions workflow
name: Automated PR Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  automated-review:
    runs-on: ubuntu-latest
    steps:
      - name: Quick PR Review
        run: |
          zen pr_review \
            --pr-url ${{ github.event.pull_request.html_url }} \
            --mode quick \
            --submit-review \
            --review-action comment

      - name: Comprehensive Review (Large PRs)
        if: github.event.pull_request.additions > 1000
        run: |
          zen pr_review \
            --pr-url ${{ github.event.pull_request.html_url }} \
            --mode thorough \
            --submit-review \
            --review-action request_changes
```

## Error Handling and Resilience

### GitHub API Resilience

**Primary → Fallback → Manual Strategy:**
```bash
# Primary: GitHub CLI
gh pr view [number] || 
# Fallback: Direct API
curl -s "https://api.github.com/repos/[owner]/[repo]/pulls/[number]" ||
# Manual: User provides PR details
echo "⚠️ GitHub unavailable - provide PR URL for manual analysis"
```

**Graceful Degradation:**
- Continues analysis with partial data when possible
- Provides clear messaging about limitations
- Offers manual analysis options when automation fails

### Model Availability Issues

**Model Testing Before Use:**
```python
# Test model availability before coordination
for model in preferred_models:
    if test_model_availability(model):
        available_models.append(model)
    else:
        log_warning(f"Model {model} unavailable, using fallback")
```

**Fallback Strategies:**
- Automatic fallback through priority model lists
- Graceful degradation to simpler analysis modes
- Clear communication about analysis limitations

### Progress Indicators

**Real-Time Feedback:**
```bash
🔍 Step 1/4: Analyzing PR structure...
⚡ Step 2/4: Running quality gates...
🤖 Step 3/4: Coordinating agents...
📝 Step 4/4: Generating report...
```

**Time Estimates:**
- Provides estimated completion time based on mode and PR size
- Updates estimates as analysis progresses
- Warns about longer analysis times for complex PRs

## Performance Optimizations

### Analysis Time Improvements

**Version 2.0 Enhancements:**
- ⚡ **5-45 minute adaptive timing** (vs. fixed 20-45 minutes)
- 🎯 **Early exit for clear cases** (quality issues > 10 → immediate feedback)
- 📊 **Large PR handling** (>20K lines → sampling strategy)
- 🔧 **Copy-paste fix commands** (actionable developer guidance)
- 🤖 **Model validation** (test availability before use)
- 📱 **Progress indicators** (real-time feedback during analysis)
- 🛡️ **Enhanced error handling** (graceful degradation strategies)

### Efficiency Strategies

**Smart Sampling:**
- Focuses on core changed files for large PRs
- Prioritizes source code over configuration/documentation
- Maintains analysis quality while reducing scope

**Parallel Processing:**
- Runs quality gates in parallel where possible
- Coordinates multiple agents simultaneously
- Optimizes I/O operations for GitHub data fetching

## Best Practices

- **Choose appropriate mode**: Use quick for small PRs, adaptive for most cases, thorough for critical changes
- **Leverage early exit**: Allow the tool to skip unnecessary analysis for clear cases
- **Focus on actionable feedback**: Use the copy-paste fix commands for efficient issue resolution
- **Security and performance awareness**: Use focused modes for specialized reviews
- **GitHub integration**: Submit reviews for team coordination and audit trails
- **Monitor analysis time**: Consider PR splitting for consistently long analysis times
- **Quality gate compliance**: Address quality issues before requesting human review

## Integration with Development Workflow

### Pre-Review Checklist

```bash
# 1. Validate PR is ready for review
zen pr_review --pr-url [URL] --mode quick --skip-quality-gates

# 2. Run comprehensive analysis
zen pr_review --pr-url [URL] --mode adaptive --include-fix-commands

# 3. Address issues with copy-paste commands
# [Run generated fix commands]

# 4. Submit for team review
zen pr_review --pr-url [URL] --mode adaptive --submit-review
```

### Team Integration

**Review Assignment:**
- Use different modes based on reviewer expertise level
- Coordinate security reviews with security-focus mode
- Performance reviews with performance-focus mode

**Quality Standards:**
- Establish team standards for quality gate thresholds
- Use consistent review modes across team
- Integrate with existing code review processes

## Technical Implementation

### Architecture Design

**BaseTool Integration:**
- Extends BaseTool for zen framework compatibility
- Uses Pydantic models for request validation
- Implements comprehensive error handling and logging

**GitHub Integration:**
- Direct subprocess calls for GitHub CLI operations
- HTTP client for GitHub API fallback
- Authentication handling with token management

**Multi-Agent Coordination:**
- Interfaces with zen consensus system for agent coordination
- Dynamic agent selection based on PR characteristics
- Model availability validation and fallback handling

### Quality Gate Implementation

**Modular Quality Checks:**
- Pluggable quality gate modules for different file types
- Configurable thresholds for different quality standards
- Extensible architecture for custom quality checks

**Early Exit Optimization:**
- Smart threshold evaluation for different modes
- Efficient quality issue aggregation and reporting
- Optimized file sampling for large PR analysis

This comprehensive PR review tool brings enterprise-grade adaptive review capabilities to the zen framework, providing intelligent scaling from quick 2-minute reviews to thorough 45-minute analysis based on PR complexity and content characteristics.