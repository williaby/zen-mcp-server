# Zen MCP Server Setup Guide

This guide covers complete setup for the Zen MCP Server with Claude Code, including WSL configuration and fork development workflow.

## Prerequisites

- WSL2 with Ubuntu (for Windows users) OR macOS/Linux
- Claude Code CLI installed (`npm install -g @anthropic/claude-code`)
- Python 3.10+ available
- Git installed

## Quick Setup

### 1. Initial Repository Setup

```bash
# Clone the repository
git clone https://github.com/BeehiveInnovations/zen-mcp-server.git
cd zen-mcp-server

# For WSL users: Fix script permissions
chmod +x run-server.sh

# For WSL users: Fix line endings if needed
dos2unix .env 2>/dev/null || true
```

### 2. Run Setup Script

```bash
./run-server.sh
```

This automatically:
- Creates virtual environment (`.zen_venv`)
- Installs all dependencies
- Sets up `.env` configuration
- Validates API keys
- Registers with Claude Code

### 3. Verify Installation

```bash
# Check MCP registration
claude mcp list

# Should show:
# zen: /path/to/zen-mcp-server/.zen_venv/bin/python /path/to/zen-mcp-server/server.py
```

## Development Fork Setup (Optional)

For custom tools development with version control and upstream synchronization:

### 1. Create GitHub Fork

1. Go to the zen-mcp-server repository on GitHub
2. Click "Fork" button (top right)
3. Choose your account as destination
4. Keep same repository name
5. ✅ Check "Copy the main branch only"

### 2. Update Local Repository

```bash
# Add your fork as new origin
git remote rename origin upstream
git remote add origin https://github.com/YOUR_USERNAME/zen-mcp-server.git

# Push current work to fork
git push -u origin main
```

### 3. Development Workflow

**Daily Development:**
```bash
# Work on custom tools
git add tools/custom/ docs/development/
git commit -m "Implement new custom tool"
git push origin main
```

**Sync with Upstream (weekly):**
```bash
# Fetch and merge upstream changes
git fetch upstream
git merge upstream/main
git push origin main
```

## Configuration

### Environment Variables

The setup script creates `.env` with:
- **OpenAI API Key**: Auto-detected from environment
- **OpenRouter API Key**: Add manually if needed
- **Custom API URLs**: For local models (Ollama)

### API Key Setup

```bash
# Add to .env file:
OPENAI_API_KEY=your-openai-key-here
OPENROUTER_API_KEY=your-openrouter-key-here

# For local models (optional):
CUSTOM_API_URL=http://localhost:11434
```

## WSL-Specific Notes

### Common Issues and Fixes

**Script Permissions:**
```bash
chmod +x run-server.sh
```

**Line Ending Issues:**
```bash
dos2unix .env
```

**Python Path Issues:**
- Setup script uses absolute paths
- Virtual environment created in `.zen_venv`
- No global Python modifications

## Verification & Testing

### Basic Functionality Test

```bash
# Check server logs
tail -f logs/mcp_server.log

# Run quality checks
./code_quality_checks.sh

# Test model evaluation
python evaluate_model.py --test basic
```

### Custom Tools Test

```bash
# Run custom tools tests (if implemented)
python tools/custom/test_quickreview.py

# Simulator tests
python communication_simulator_test.py --quick
```

## Troubleshooting

### Common Issues

**MCP Registration Failed:**
```bash
# Manual registration
claude mcp add zen -s user -- /full/path/to/.zen_venv/bin/python /full/path/to/server.py
```

**API Key Issues:**
- Check `.env` file exists and has correct keys
- Verify keys are valid with test requests
- Check logs for authentication errors

**Virtual Environment Issues:**
```bash
# Recreate virtual environment
rm -rf .zen_venv
./run-server.sh
```

**WSL Path Issues:**
- Use absolute paths in MCP registration
- Ensure scripts have execute permissions
- Check for Windows line endings in config files

## Next Steps

1. **Test Installation**: Verify MCP tools work in Claude Code
2. **Configure API Keys**: Add your API keys to `.env`
3. **Explore Tools**: Try built-in tools like `chat`, `analyze`, `debug`
4. **Custom Development**: Use fork workflow for custom tools
5. **Join Development**: Contribute to upstream repository

## Support

- Check `CLAUDE.md` for development commands
- Review `docs/development/` for architecture
- See logs in `logs/` directory for debugging
- Use simulator tests for validation

This setup provides a complete development environment with optional fork workflow for custom tools development while maintaining upstream synchronization.