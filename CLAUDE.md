# Zen MCP Server Development Guide

> This project extends the global CLAUDE.md standards. Only project-specific configurations and deviations are documented below.

## Project-Specific Commands

> Reference: Global quality/testing commands apply. Project-specific commands below.

### Server Management
```bash
# Setup/Update server (handles venv, deps, .env, MCP config)
./run-server.sh

# View logs in real-time
./run-server.sh -f
tail -f logs/mcp_server.log
```

### Testing Framework
```bash
# Primary quality check (linting, formatting, unit tests)
./code_quality_checks.sh

# Quick validation (6 essential tests)
python communication_simulator_test.py --quick

# Integration tests (free local models via Ollama)
./run_integration_tests.sh
```

### Log Analysis
```bash
# Main server log (all activity)
tail -f logs/mcp_server.log

# Tool activity only  
tail -f logs/mcp_activity.log | grep -E "(TOOL_CALL|TOOL_COMPLETED|ERROR)"
```

## Development Workflow

> Reference: Global git workflow applies. Project-specific steps below.

**Before Changes:**
1. `source .zen_venv/bin/activate`
2. `./code_quality_checks.sh`

**After Changes:**
1. `./code_quality_checks.sh`
2. `python communication_simulator_test.py --quick`
3. Restart Claude session for code changes

**Before PR:**
1. `./run_integration_tests.sh`
2. All tests must pass 100%

## Project Architecture

### Key Files
- `./code_quality_checks.sh` - All-in-one quality validation
- `communication_simulator_test.py` - End-to-end MCP testing
- `tools/custom/` - Plugin-style tools (zero merge conflicts)
- `providers/` - AI provider implementations

### Environment
- **Python**: 3.9+ with `.zen_venv/` virtual environment
- **API Keys**: Configure in `.env` file
- **Local Testing**: Ollama + `CUSTOM_API_URL="http://localhost:11434"`

### Protected Development
- `docs/development/adrs/` - Architecture Decision Records
- `tools/custom/` - Custom tools (local until PR-ready)
- Use `.git/info/exclude` to prevent accidental staging

## Testing Notes

**Quick Test Mode (6 essential tests):**
- Cross-tool conversation memory
- Core conversation threading
- Consensus/CodeReview/Planner workflows
- Token allocation validation

**Integration Tests:** Free local models via Ollama (no API costs)

**Important:** Restart Claude session after any code changes for MCP updates to take effect.