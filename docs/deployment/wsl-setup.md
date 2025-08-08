# Claude Code WSL Setup Guide

This document covers the specific setup steps and changes needed to configure the Zen MCP Server with Claude Code in a WSL Ubuntu environment.

## Overview

Setting up the Zen MCP Server with Claude Code in WSL requires a few specific steps beyond the standard installation process. This guide documents the complete setup process and any modifications made from the base repository.

## Prerequisites

- WSL2 with Ubuntu installed
- Claude Code CLI installed (`npm install -g @anthropic/claude-code`)
- Python 3.10+ available in WSL
- Git installed

## Setup Process

### 1. Initial Repository Setup

```bash
# Clone the repository
git clone https://github.com/BeehiveInnovations/zen-mcp-server.git
cd zen-mcp-server
```

### 2. Script Permissions

The setup script may not have execute permissions in WSL. Fix this:

```bash
# Make the setup script executable
chmod +x run-server.sh
```

### 3. Line Ending Issues

WSL may have issues with Windows line endings in the `.env` file. Fix this:

```bash
# Convert line endings if dos2unix is available
dos2unix .env 2>/dev/null || true
```

### 4. Run Setup Script

```bash
# Run the setup script
./run-server.sh
```

This script will:
- Clear Python cache files
- Create virtual environment (`.zen_venv`)
- Install all dependencies
- Set up `.env` configuration
- Validate API keys

### 5. Register with Claude Code

The setup script attempts to register automatically, but you can do it manually:

```bash
# Register the MCP server with Claude Code
claude mcp add zen -s user -- /home/byron/dev/zen-mcp-server/.zen_venv/bin/python /home/byron/dev/zen-mcp-server/server.py
```

### 6. Verify Registration

```bash
# List configured MCP servers
claude mcp list

# Should show:
# zen: /home/byron/dev/zen-mcp-server/.zen_venv/bin/python /home/byron/dev/zen-mcp-server/server.py
```

## Configuration Changes Made

### Environment File (.env)

The following API keys were configured:

1. **OpenAI API Key**: Automatically detected from environment and added to `.env`
2. **OpenRouter API Key**: Added manually (see Configuration section below)

### Virtual Environment

- Created `.zen_venv` directory with Python 3.12
- Installed all required dependencies via pip
- No global Python packages modified

### MCP Registration

- Registered with Claude Code using absolute paths
- Uses the virtual environment Python interpreter
- Server script path: `/home/byron/dev/zen-mcp-server/server.py`

## Files Modified

1. **`.env`**: Added API keys and configuration
2. **File permissions**: Made `run-server.sh` executable
3. **Line endings**: Fixed Windows CRLF to Unix LF format

## Available Tools

After setup, the following tools are available through the zen MCP server:

- `chat`: AI conversations and assistance
- `thinkdeep`: Extended reasoning with AI models
- `planner`: Project planning and task breakdown
- `consensus`: Multi-model consensus building
- `codereview`: Code review and suggestions
- `debug`: Code debugging assistance
- `analyze`: Code analysis and insights
- `refactor`: Code refactoring suggestions
- `testgen`: Test generation
- `secaudit`: Security auditing
- `docgen`: Documentation generation
- `tracer`: Code tracing and analysis
- `challenge`: Challenge verification
- `listmodels`: List available AI models
- `version`: Show server version

## Troubleshooting

### Common Issues

1. **Permission Denied**: Make sure `run-server.sh` is executable
   ```bash
   chmod +x run-server.sh
   ```

2. **Line Ending Issues**: Convert file formats if needed
   ```bash
   dos2unix .env
   ```

3. **Python Import Errors**: Clear cache and restart
   ```bash
   ./run-server.sh --clear-cache
   ```

4. **MCP Server Not Found**: Verify registration
   ```bash
   claude mcp list
   ```

### Logs

View server logs for debugging:

```bash
# Follow logs in real-time
tail -f /home/byron/dev/zen-mcp-server/logs/mcp_server.log

# View recent activity
tail -n 100 /home/byron/dev/zen-mcp-server/logs/mcp_activity.log
```

## Server Behavior

- **On-Demand**: Server only starts when Claude Code needs it
- **Automatic**: No manual startup/shutdown required
- **Persistent**: Registration survives WSL restarts
- **Resource Efficient**: Only runs during active use

## Next Steps

1. **Restart Claude Code session** to load the new MCP server
2. **Test tools**: Try using zen tools in your next Claude Code session
3. **Configure models**: Set up custom models if needed (see `docs/custom_models.md`)
4. **Update regularly**: See "Updating from Remote" section below for safe update procedures

## Support

For issues specific to WSL setup:
1. Check the logs in `/home/byron/dev/zen-mcp-server/logs/`
2. Verify Python virtual environment is working
3. Ensure Claude Code CLI is properly installed
4. Check MCP server registration with `claude mcp list`

For general Zen MCP Server issues, refer to the main documentation in the repository.

## Updating from Remote Repository

This local installation maintains custom modifications alongside the upstream repository. When updating, you need to handle both local changes and incoming remote changes carefully.

### Before Updating: Check What's Coming

```bash
# Fetch remote changes without merging
git fetch origin

# See what files have incoming changes
git diff HEAD origin/main --name-only

# Check specific file changes that might conflict
git diff HEAD origin/main server.py
git diff HEAD origin/main conf/custom_models.json
```

### Safe Update Procedure

#### Option 1: Stash Method (Recommended for Complex Conflicts)

```bash
# 1. Save your local changes temporarily
git stash push -m "Local customizations before pull"

# 2. Pull remote changes cleanly
git pull origin main

# 3. Re-apply your local changes
git stash pop

# 4. If conflicts occur, resolve them manually
# Files with conflicts will have conflict markers like:
# <<<<<<< HEAD
# Your local changes
# =======
# Remote changes  
# >>>>>>> Stashed changes

# 5. After resolving conflicts, restart the server
./run-server.sh
```

#### Option 2: Direct Pull (For Non-Conflicting Changes)

```bash
# Pull remote changes directly
git pull origin main

# If automatic merge succeeds, restart server
./run-server.sh
```

### Handling Merge Conflicts

When conflicts occur, you'll see conflict markers in affected files:

```
<<<<<<< HEAD (remote changes)
remote code here
=======
your local code here  
>>>>>>> main (your local changes)
```

**Resolution Steps:**
1. **Edit each conflicting file** to keep the changes you want
2. **Remove conflict markers** (`<<<<<<<`, `=======`, `>>>>>>>`)
3. **Keep your custom functionality** (like QuickReview tool, custom models)
4. **Integrate useful remote improvements** 
5. **Test the resolution**: `./run-server.sh`
6. **Commit the merge**: `git add . && git commit -m "Merge remote changes with local customizations"`

### Local Files That Should Always Be Preserved

These files contain your custom modifications and should typically keep local changes:

- **`conf/custom_models.json`**: Your custom model configurations
- **`tools/quickreview.py`**: Custom QuickReview tool
- **`systemprompts/quickreview_prompt.py`**: Custom system prompt  
- **`server.py`**: QuickReview tool registration and OpenAI o3 references
- **`tools/__init__.py`** & **`systemprompts/__init__.py`**: QuickReview exports
- **`tools/listmodels.py`**: Enhanced model display functionality
- **All files in `docs/`**: Your custom documentation
- **`PromptCraft/` and `PromptCraft-work/`**: Separate projects (untracked)

### Post-Update Checklist

After any update:

1. **Restart Claude Code session** to load updated server
2. **Test core functionality**: Try a few zen tools to ensure they work
3. **Check logs** for any new errors: `tail -f logs/mcp_server.log`
4. **Verify custom tools**: Test QuickReview tool specifically
5. **Run quality checks** if you made manual conflict resolutions:
   ```bash
   ./code_quality_checks.sh
   ```

### Troubleshooting Update Issues

**If server won't start after update:**
```bash
# Check for Python dependency issues
./run-server.sh --clear-cache

# View detailed error logs  
tail -n 50 logs/mcp_server.log

# Verify virtual environment integrity
source .zen_venv/bin/activate
python -c "import server; print('Import successful')"
```

**If conflicts seem too complex:**
```bash
# Reset to clean state and manually re-add customizations
git reset --hard origin/main

# Then manually re-add your customizations:
# - Custom model configs
# - QuickReview tool files
# - Documentation updates
```

This update strategy preserves your valuable local customizations while staying current with upstream improvements.