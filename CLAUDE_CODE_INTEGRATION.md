# Claude Code Integration Guide

## Overview

This document describes the changes made to Claude Code configuration to integrate with the Zen MCP Hub for 80-90% context reduction.

## Configuration Changes Made

### 1. Updated Zen Server Configuration

**File**: `/home/byron/.claude/mcp/zen-server.json`

**Before** (Individual Server):
```json
{
  "mcpServers": {
    "zen": {
      "command": "/home/byron/dev/zen-mcp-server/.zen_venv/bin/python",
      "args": ["/home/byron/dev/zen-mcp-server/server.py"]
    }
  }
}
```

**After** (Hub Server):
```json
{
  "mcpServers": {
    "zen-hub": {
      "command": "/home/byron/dev/zen-mcp-server/.zen_venv/bin/python",
      "args": ["/home/byron/dev/zen-mcp-server/hub_server.py"],
      "env": {
        "ZEN_HUB_ENABLED": "true",
        "ZEN_HUB_FILTERING": "true",
        "ZEN_HUB_MAX_TOOLS": "25",
        "ZEN_HUB_DETECTION_TIMEOUT": "5",
        "ZEN_HUB_LOGGING": "true"
      }
    }
  }
}
```

### 2. Disabled Individual MCP Servers

The following servers are now accessed through the hub instead of directly:

- **`dev-tools-servers.json`** → **`dev-tools-servers.json.disabled`**
  - Contains: git, time, sequential-thinking servers
  - Now handled by hub's MCP client manager

- **`context7-sse.json`** → **`context7-sse.json.disabled`**
  - Contains: context7-sse server
  - Now handled by hub's SSE client connections

### 3. Backup Created

Original configurations backed up to:
```
/home/byron/.claude/mcp-backup-{timestamp}/
```

## Environment Variables

The hub server supports the following environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `ZEN_HUB_ENABLED` | `true` | Enable/disable hub functionality |
| `ZEN_HUB_FILTERING` | `true` | Enable/disable dynamic tool filtering |
| `ZEN_HUB_MAX_TOOLS` | `25` | Maximum tools per context |
| `ZEN_HUB_DETECTION_TIMEOUT` | `5` | Tool detection timeout (seconds) |
| `ZEN_HUB_CLIENT_TIMEOUT` | `30` | MCP client timeout (seconds) |
| `ZEN_HUB_CACHE` | `true` | Enable detection result caching |
| `ZEN_HUB_CACHE_TTL` | `300` | Cache TTL (seconds) |
| `ZEN_HUB_LOGGING` | `true` | Enable hub-specific logging |
| `ZEN_HUB_FILTER_LOGGING` | `false` | Enable detailed filter logging |

## How It Works

1. **Single Connection**: Claude Code now connects only to the `zen-hub` server
2. **Query Analysis**: Hub analyzes each query to determine relevant tool categories
3. **Dynamic Filtering**: Only relevant tools are loaded into the context
4. **Tool Routing**: Tool calls are routed to the appropriate external MCP server
5. **Fallback**: If filtering fails, falls back to core tools or all tools

## Tool Categories

The hub categorizes tools into the following groups:

- **development**: Debug, code review, analysis tools
- **workflow**: Git, planning, consensus tools  
- **specialized**: Security, performance analysis tools
- **utilities**: Time, basic utilities

## Expected Behavior

- **Faster Response**: Reduced context means faster Claude responses
- **Smart Loading**: Only relevant tools appear for each query type
- **Transparent**: No user-visible changes in functionality
- **Reliable**: Fallback mechanisms ensure tools are always available

## Troubleshooting

### To Disable Hub (Fallback to Original)

1. Restore original configuration:
   ```bash
   cp /home/byron/.claude/mcp-backup-*/zen-server.json /home/byron/.claude/mcp/
   ```

2. Re-enable individual servers:
   ```bash
   mv /home/byron/.claude/mcp/dev-tools-servers.json.disabled /home/byron/.claude/mcp/dev-tools-servers.json
   mv /home/byron/.claude/mcp/context7-sse.json.disabled /home/byron/.claude/mcp/context7-sse.json
   ```

### To Debug Hub Issues

Set environment variable:
```bash
export ZEN_HUB_LOGGING=true
export ZEN_HUB_FILTER_LOGGING=true
```

### To Disable Filtering Only

Set in configuration:
```json
"env": {
  "ZEN_HUB_ENABLED": "true",
  "ZEN_HUB_FILTERING": "false"
}
```

This will use the hub but load all tools (no filtering).

## Status Verification

To verify the hub is working, check Claude Code behavior:
- Responses should be faster
- Tool availability should vary by query type
- All functionality should remain intact

The hub implementation maintains full backward compatibility while providing massive context reduction benefits.