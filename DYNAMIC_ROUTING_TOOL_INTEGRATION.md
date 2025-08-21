# Dynamic Routing - Tool Integration Guide

> How to leverage dynamic model routing with existing Zen MCP Server tools for optimal cost and performance.

## 🎯 Overview

The dynamic model routing system seamlessly integrates with **all existing tools** through transparent model provider wrapping. When enabled, every tool automatically benefits from:

- **Free model prioritization** (29 free models available)
- **Complexity-based routing** (simple tasks → free models, complex tasks → premium models) 
- **Cost optimization** (20-30% typical savings)
- **Intelligent fallback** (automatic escalation if needed)

## 🚀 Quick Start

### Enable Routing
```bash
export ZEN_SMART_ROUTING=true
./run-server.sh
```

### Verify Integration
```bash
# Check routing status
routing_status action=status

# View available models by level
routing_status action=models
```

## 🛠️ Tool-by-Tool Integration

### Chat & General Purpose Tools

#### `mcp__zen__chat`
- **Routing Strategy**: Prioritizes free models for general conversation
- **Complexity Triggers**: Technical discussions, code explanations → Junior level
- **Free Model Selection**: `qwen/qwen-2.5-coder-32b-instruct:free` for coding topics

**Example Usage:**
```bash
# General chat - routes to free model
chat prompt="Explain Python decorators" model=auto

# Complex architectural discussion - may route to senior level
chat prompt="Design a microservices architecture for high-frequency trading" model=auto
```

#### `mcp__zen__thinkdeep`
- **Routing Strategy**: Complexity analysis determines model level
- **Typical Routing**: Senior/Executive for multi-step reasoning
- **Cost Impact**: Automatically balances depth vs cost

### Code Analysis Tools

#### `mcp__zen__codereview`
- **Routing Strategy**: File count + complexity determines level
- **Small PRs (1-5 files)**: Junior level (`claude-3-haiku`, `gemini-flash`)
- **Large PRs (10+ files)**: Senior level (`claude-3-sonnet`, `gemini-pro`)
- **Security-focused**: Executive level for critical analysis

**Routing Triggers:**
```python
# Simple code review - Junior level
files_checked = ["utils.py", "helpers.py"]  # → Junior

# Complex system review - Senior level  
files_checked = ["auth.py", "security.py", "payment.py"]  # → Senior

# Security audit - Executive level
findings = [{"severity": "critical"}]  # → Executive
```

#### `mcp__zen__debug`
- **Routing Strategy**: Error complexity + context determines level
- **Simple bugs**: Free models (`deepseek-chat:free`)
- **Complex race conditions**: Senior level
- **Critical production issues**: Executive level

**Example Routing:**
```bash
# Simple syntax error - Free model
debug step="Fix TypeError in user validation" 

# Complex concurrency bug - Senior model
debug step="Investigate race condition in payment processing"
```

#### `mcp__zen__refactor`
- **Routing Strategy**: Code size + refactoring type
- **Code smells**: Junior level
- **Architecture refactoring**: Senior level
- **Legacy modernization**: Executive level

### Security & Compliance Tools

#### `mcp__zen__secaudit`
- **Routing Strategy**: Always prioritizes security-capable models
- **Minimum Level**: Junior (security-aware models only)
- **OWASP Analysis**: Senior level minimum
- **Compliance Review**: Executive level

**Security Model Filtering:**
```python
# Only security-capable models selected
security_models = [
    "claude-3-sonnet",      # Senior - security analysis
    "gpt-4",               # Executive - comprehensive security
    "claude-opus"          # Executive - expert security review
]
```

#### `mcp__zen__precommit`
- **Routing Strategy**: Change scope determines model level
- **Small commits**: Junior level
- **Multi-file changes**: Senior level  
- **Breaking changes**: Executive level validation

### Documentation Tools

#### `mcp__zen__docgen`
- **Routing Strategy**: Documentation scope + complexity
- **API docs**: Junior level sufficient
- **Architecture docs**: Senior level for technical depth
- **Complete system docs**: Executive level

### Consensus & Planning Tools

#### `mcp__zen__consensus`
- **Routing Strategy**: Uses specified models + free alternatives
- **Free Model Injection**: Adds free models to consensus pool
- **Cost Optimization**: Replaces expensive models with capable free alternatives

**Enhanced Consensus:**
```bash
# Original request
consensus models='["gpt-4", "claude-opus"]'

# Routing enhancement - adds free models
models_used = ["gpt-4", "claude-opus", "qwen-coder-32b:free", "deepseek-chat:free"]
```

#### `mcp__zen__planner`
- **Routing Strategy**: Planning complexity determines model level
- **Simple feature planning**: Junior level
- **System architecture**: Senior level
- **Strategic roadmaps**: Executive level

### Testing & Quality Tools

#### `mcp__zen__testgen`
- **Routing Strategy**: Test complexity + coverage requirements
- **Unit tests**: Free/Junior models sufficient
- **Integration tests**: Senior level for complex scenarios
- **End-to-end test suites**: Executive level

## 📊 Routing Decision Matrix

| Tool Category | Simple Tasks | Moderate Tasks | Complex Tasks | Critical Tasks |
|---------------|-------------|----------------|---------------|----------------|
| **Chat/General** | Free (qwen-coder) | Junior (haiku) | Senior (sonnet) | Executive (opus) |
| **Code Review** | Junior (1-3 files) | Senior (4-10 files) | Senior (10+ files) | Executive (security) |
| **Debug** | Free (syntax errors) | Junior (logic bugs) | Senior (race conditions) | Executive (production) |
| **Security** | Junior (basic scan) | Senior (OWASP) | Executive (compliance) | Executive (audit) |
| **Documentation** | Junior (API docs) | Senior (architecture) | Executive (system docs) | Executive (specifications) |

## 🎛️ Customization & Control

### Tool-Specific Routing Rules

Edit `routing/model_routing_config.json` to customize per-tool behavior:

```json
{
  "tool_specific_rules": {
    "mcp__zen__secaudit": {
      "minimum_level": "senior",
      "prefer_security_models": true,
      "cost_override": false
    },
    "mcp__zen__chat": {
      "prefer_free": true,
      "max_cost_per_token": 0.0001
    },
    "mcp__zen__codereview": {
      "file_count_thresholds": {
        "junior": 5,
        "senior": 15,
        "executive": 50
      }
    }
  }
}
```

### Force Specific Routing Level

Override routing decisions when needed:

```bash
# Force free model for testing
ZEN_ROUTING_LEVEL=free codereview step="Test with free model"

# Force executive level for critical analysis  
ZEN_ROUTING_LEVEL=executive secaudit step="Production security audit"
```

### Monitor Routing Decisions

Track how routing affects your tools:

```bash
# View routing statistics per tool
routing_status action=stats

# Get recommendation for specific tool usage
routing_status action=recommend prompt="Code review for payment system" context='{"tool_name":"codereview","files":["payment.py","billing.py"]}'
```

## 💰 Cost Impact Examples

### Before Dynamic Routing
```
codereview (10 files) → claude-opus-4 → $0.0150 per request
debug (simple error) → gpt-4 → $0.0030 per request  
chat (general help) → claude-sonnet → $0.0030 per request
```

### After Dynamic Routing
```
codereview (10 files) → claude-sonnet → $0.0030 per request (-80%)
debug (simple error) → qwen-coder:free → $0.0000 per request (-100%)
chat (general help) → deepseek-chat:free → $0.0000 per request (-100%)
```

**Typical Savings: 20-30% overall cost reduction**

## 🔍 Advanced Integration Patterns

### Multi-Tool Workflows

Dynamic routing optimizes entire workflow costs:

```bash
# Research → Analysis → Implementation workflow
1. chat (research) → free model
2. thinkdeep (analysis) → senior model  
3. codereview (validation) → junior model
```

### Context-Aware Routing

Routing considers cross-tool context:

```python
# Previous tool context influences routing
context = {
    "previous_tool": "secaudit",
    "findings": [{"severity": "high"}],
    "files": ["auth.py"]
}
# → Routes subsequent tools to security-capable models
```

### Fallback Chains

Automatic escalation when models fail:

```
Free Model → Junior → Senior → Executive
  ↓           ↓        ↓         ↓
Retry      Escalate  Escalate  Human
```

## 🚨 Important Notes

### When Routing is Bypassed

- **Explicit model parameter**: `model="claude-opus"` bypasses routing
- **Tool requirements**: Some tools may require specific model capabilities
- **Failure handling**: Routing falls back to original model selection on errors

### Performance Considerations

- **Decision time**: < 50ms routing overhead
- **Cache efficiency**: Repeated similar requests use cached decisions
- **Memory usage**: Minimal impact on server memory

### Security Implications

- **Model filtering**: Security tools only route to security-capable models
- **Audit trails**: All routing decisions are logged for compliance
- **Fallback safety**: System never routes down from required security levels

## 🎉 Best Practices

1. **Let routing work**: Don't specify explicit models unless required
2. **Monitor patterns**: Use `routing_status` to understand routing behavior  
3. **Customize wisely**: Adjust thresholds based on your usage patterns
4. **Test thoroughly**: Verify routing works for your specific tool combinations
5. **Cost awareness**: Monitor savings and adjust free model preferences

## 📞 Support & Troubleshooting

### Common Issues

**Routing not working?**
```bash
# Check if routing is enabled
routing_status action=status

# Verify environment variable
echo $ZEN_SMART_ROUTING
```

**Unexpected model selection?**
```bash
# Get explanation for routing decision
routing_status action=recommend prompt="Your prompt here" context='{"files":["your_file.py"]}'
```

**Want to customize routing?**
- Edit `routing/model_routing_config.json`
- Restart server: `./run-server.sh`
- Verify changes: `routing_status action=config`

---

*Dynamic routing enhances all existing tools transparently. Enable it once, benefit everywhere!*