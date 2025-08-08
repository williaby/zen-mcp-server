# Local Customizations for Zen MCP Server

This document outlines how to maintain custom tools and modifications in the Zen MCP Server while preserving the ability to pull upstream changes from the source repository without conflicts.

## Overview

### Strategy: Additive-Only Customizations
- **Core Principle**: Add new files without modifying existing core logic
- **Git Compatibility**: Maintain clean pulls from upstream repository
- **Isolation**: Keep custom functionality separate from upstream code
- **Documentation**: Track all customizations for upgrade safety

### Benefits
- Seamless upstream updates via `git pull`
- Preserved custom functionality across upgrades  
- Clear separation of custom vs upstream code
- Maintainable development workflow

## Custom Tool Development Process

### Method 1: Plugin-Style Architecture (RECOMMENDED)
**Zero-Conflict Approach** - Use the isolated `tools/custom/` directory system:

```bash
# Create new custom tool in isolated directory
touch tools/custom/your_custom_tool.py

# No core file modifications needed!
```

**Benefits**:
- ✅ **Zero merge conflicts** - No core file modifications required
- ✅ **Auto-discovery** - Tools automatically registered without manual steps
- ✅ **Git-independent** - Custom tools preserved across all upstream changes
- ✅ **Isolated testing** - Self-contained test files in custom directory

#### Plugin Architecture Implementation

##### A. Tool Structure
```python
# tools/custom/your_custom_tool.py
"""
Self-contained custom tool implementation
"""
from tools.workflow.base import WorkflowTool  # or SimpleTool
from tools.shared.base_models import WorkflowRequest

class YourCustomToolRequest(WorkflowRequest):
    """Custom request model with tool-specific fields"""
    # Define your parameters here
    pass

class YourCustomTool(WorkflowTool):  # or SimpleTool
    """Self-contained custom tool with embedded system prompt"""
    
    # Embedded system prompt (no external files needed)
    SYSTEM_PROMPT = """Your custom system prompt here..."""
    
    def get_name(self) -> str:
        return "your_custom_tool"
    
    def get_description(self) -> str:
        return "Your tool description"
    
    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT
    
    # Implement all required methods...
```

##### B. Auto-Discovery System
The plugin system automatically discovers and registers tools:

```python
# tools/custom/__init__.py (already implemented)
def discover_custom_tools() -> Dict[str, BaseTool]:
    """Automatically discover and instantiate custom tools"""
    # Scans tools/custom/ directory for tool implementations
    # No manual registration needed!
```

##### C. Minimal Integration
Only **5 lines** added to `server.py` for all custom tools:

```python
# Load custom tools from tools/custom directory
try:
    from tools.custom import get_custom_tools
    custom_tools = get_custom_tools()
    TOOLS.update(custom_tools)
except ImportError:
    pass  # No custom tools available
```

##### D. MCP Interface Optimization
**Critical**: The MCP interface in Claude Code's "View Tools" shows ALL schema parameters to users. Workflow tools inherit many internal fields that create overwhelming interfaces.

**Problem**: Base WorkflowRequest includes 15+ internal fields (step, findings, files_checked, etc.)
**Solution**: Use custom `get_input_schema()` with excluded fields for clean user interfaces.

```python
# Custom schema with excluded fields for clean MCP interface
def get_input_schema(self) -> dict[str, Any]:
    """Generate clean input schema with minimal user-facing parameters."""
    from tools.workflow.schema_builders import WorkflowSchemaBuilder
    
    # Tool-specific fields - only essential user parameters
    tool_field_overrides = {
        "your_param": {
            "type": "string",
            "description": "User-friendly description",
        },
    }

    # Hide complex internal fields from MCP interface
    excluded_workflow_fields = [
        "files_checked",         # Managed internally
        "relevant_context",      # Managed internally  
        "issues_found",          # Managed internally
        "hypothesis",            # Internal workflow state
        "backtrack_from_step",   # Advanced workflow control
        "confidence",            # Internal assessment
        "use_assistant_model",   # Tool-specific behavior
    ]
    
    excluded_common_fields = [
        "use_websearch",         # Always enabled by default
    ]

    return WorkflowSchemaBuilder.build_schema(
        tool_specific_fields=tool_field_overrides,
        required_fields=["your_required_param"],
        excluded_workflow_fields=excluded_workflow_fields,
        excluded_common_fields=excluded_common_fields,
        tool_name=self.get_name(),
    )
```

**Results**: QuickReview reduced from 19 to 12 parameters (37% reduction) for cleaner MCP interface.

### Method 2: Traditional Approach (Legacy)
**Higher Conflict Risk** - Direct core file modifications:

#### A. Tool Registration in `tools/__init__.py`
```python
# ADD to imports section:
from .your_custom_tool import YourCustomTool

# ADD to __all__ list:
__all__ = [
    # ... existing tools ...
    "YourCustomTool",  # ADD THIS LINE
]
```

#### B. Server Registration in `server.py`
```python
# ADD to TOOLS dictionary:
TOOLS = {
    # ... existing tools ...
    "your_custom_tool": YourCustomTool(),  # ADD THIS LINE
}
```

**⚠️ Warning**: This approach requires core file modifications and may cause merge conflicts.

## Testing Custom Tools

### Plugin-Style Testing (Recommended)
Create self-contained test files in the custom directory:

```python
# tools/custom/test_your_custom_tool.py
"""Self-contained test for custom tool"""
import tempfile
from pathlib import Path

class CustomYourToolTest:
    """Test custom tool functionality"""
    
    def run_basic_test(self) -> bool:
        """Run basic validation test"""
        try:
            # Test tool instantiation
            from tools.custom.your_custom_tool import YourCustomTool
            tool = YourCustomTool()
            
            # Test tool properties
            assert tool.get_name() == "your_custom_tool"
            assert tool.get_description()
            
            # Test successful
            return True
            
        except Exception as e:
            print(f"Custom tool test failed: {e}")
            return False

if __name__ == "__main__":
    test = CustomYourToolTest()
    success = test.run_basic_test()
    exit(0 if success else 1)
```

### Integration Testing
Add simulator tests for end-to-end validation:

```python
# Add to communication_simulator_test.py
def test_your_custom_tool_validation(self):
    """Test your custom tool with real API calls"""
    response = self.call_tool("your_custom_tool", {
        "param1": "test_value",
        "model": "flash"
    })
    self.validate_response_structure(response)
```

### Run Tests
```bash
# Test custom tool directly (plugin style)
python tools/custom/test_your_custom_tool.py

# Test specific custom tool via simulator
python communication_simulator_test.py --individual your_custom_tool_validation

# Run comprehensive test suite including custom tools
python communication_simulator_test.py --quick
```

## Git Pull Compatibility Strategy

### Pre-Pull Checklist
1. **Backup Custom Tools**: Ensure all custom tools are documented below
2. **Test Current State**: Run `./code_quality_checks.sh` to ensure clean baseline
3. **Document Dependencies**: Note any model configuration dependencies

### Pull Process
```bash
# Standard git pull (should work without conflicts)
git pull origin main

# Verify custom tools still registered
grep -A 20 "TOOLS = {" server.py | grep your_custom_tool

# Verify imports still present  
grep "your_custom_tool" tools/__init__.py
```

### Post-Pull Validation
```bash
# Run quality checks
./code_quality_checks.sh

# Test custom tools
python communication_simulator_test.py --quick

# Verify server starts correctly
./run-server.sh

# Check logs for any issues
tail -n 50 logs/mcp_server.log
```

### Conflict Resolution
If conflicts occur (rare with additive-only approach):

1. **Tool Files**: Custom tool files should never conflict
2. **Registration Points**: If `__init__.py` or `server.py` conflicts:
   ```bash
   # Accept upstream changes
   git checkout --theirs tools/__init__.py server.py
   
   # Re-add custom tool registrations
   # (Use this document's registry as reference)
   ```

## Model Configuration Dependencies

### Dynamic Model Selection
Custom tools should use dynamic model selection to handle model configuration changes:

```python
def get_models_by_tier(tier):
    """Get models dynamically from current configuration"""
    from docs.current_models import get_current_models  # Hypothetical
    
    models = get_current_models()
    
    if tier == "free":
        return [m for m in models if m.output_cost == 0]
    elif tier == "value":
        return [m for m in models if 0 < m.output_cost <= 10]
    else:  # premium
        return models
```

### Configuration References
- **Current Models**: [current_models.md](./current_models.md) (Updated regularly)
- **Model Selection**: Reference this file for tier-appropriate model selection
- **Cost Tracking**: Use dynamic pricing from configuration

## Reference Documentation

### Core Architecture
- [Adding Tools Guide](./adding_tools.md) - Complete tool development guide
- [Advanced Usage](./advanced-usage.md) - Tool usage patterns and examples
- [Claude Development Guide](../CLAUDE.md) - Development workflow and commands

### Example Implementations
- [Consensus Tool](../tools/consensus.py) - Multi-model workflow example
- [Chat Tool](../tools/chat.py) - Simple tool example
- [Code Review Tool](../tools/codereview.py) - Complex workflow example

### Testing and Quality
- [Communication Simulator Tests](../communication_simulator_test.py) - End-to-end testing framework
- [Code Quality Scripts](../code_quality_checks.sh) - Automated quality validation

## Custom Tool Registry

This section documents all custom tools added to this local installation:

### Currently Implemented Custom Tools

#### QuickReview Tool (✅ IMPLEMENTED)
- **`quickreview`**: Basic validation using free models (2-3 models)
  - Purpose: Grammar, syntax, basic code validation, documentation review
  - Models: Free tier models only (cost = $0)
  - Features: Dynamic model selection, robust availability handling, role-based analysis
  - Cost: $0/session
  - Usage: `quickreview proposal:"Check this code syntax" files:["src/auth.py"] focus:"syntax"`
  - Dependencies: Dynamic free model selection from current_models.md
  - Status: ✅ Fully implemented and tested
  - **Architecture**: Plugin-style (zero merge conflicts)
  - **MCP Interface**: Optimized from 19 to 12 parameters (37% reduction)
  - **Files**: 
    - `tools/custom/quickreview.py` - Main implementation (507 lines)
    - `tools/custom/test_quickreview.py` - Self-contained tests (77 lines)
    - `tools/custom/__init__.py` - Auto-discovery system (44 lines)
    - `tools/tmp/quickreview.md` - Architecture Decision Record
  - **Integration**: Minimal server.py modification (5 lines only)
  - **Interface Optimization**: Custom `get_input_schema()` excludes 7 internal fields

### Currently Planned Custom Tools

#### Tiered Review Tools (In Development)

- **`review`**: Peer review panel using value models (5-7 models)  
  - Purpose: Development reviews, PR analysis, troubleshooting
  - Models: Value tier models (≤$10 output/M)
  - Roles: Security, Development, Architecture, Operations
  - Cost: Moderate
  - **Architecture**: Plugin-style (zero merge conflicts)
  - **ADR**: `tools/tmp/review.md` - Complete architecture plan

- **`criticalreview`**: Critical decision analysis using premium models (6+ models)
  - Purpose: Major design decisions, root cause analysis, comprehensive remediation
  - Models: All tiers including premium
  - Roles: Lead Architect, Technical Director, Security Chief, Research Lead, System Integration, Risk Analysis
  - Cost: Premium
  - **Architecture**: Plugin-style (zero merge conflicts)
  - **ADR**: `tools/tmp/criticalreview.md` - Complete architecture plan

**Dependencies**: 
- Dynamic model selection from [current_models.md](./current_models.md)
- Role-based analysis system
- Cost tracking and budget controls

**Development Workspace**: 
- **`tools/tmp/`** - ⚠️ **PROTECTED DIRECTORY** - Contains critical ADRs
  - `tools/tmp/review.md` - Review tool architecture plan
  - `tools/tmp/criticalreview.md` - CriticalReview tool architecture plan
  - `tools/tmp/future.md` - Future enhancements roadmap
  - `tools/tmp/prepare-pr.md` - PR preparation checklist
  - `tools/tmp/README.md` - Directory protection guide

### Adding New Tools to Registry
When adding custom tools, document:
1. **Tool Name**: CLI command name
2. **Purpose**: What problem it solves
3. **Parameters**: Required and optional parameters
4. **Model Requirements**: Which models/tiers it uses
5. **Dependencies**: Configuration files, other tools, etc.
6. **Usage Examples**: Common use cases

### Upgrade Notes
- **Model Changes**: Tools automatically adapt to model configuration changes
- **Version Compatibility**: All custom tools tested with each upstream pull
- **Breaking Changes**: Monitor upstream releases for breaking changes to base classes

## Development Workflow

### Adding a New Custom Tool (Plugin-Style - Recommended)
1. **Design**: Plan tool purpose, parameters, and architecture
2. **Implement**: Create tool file in `tools/custom/your_tool.py`
3. **Optimize MCP Interface**: Override `get_input_schema()` to exclude internal fields
4. **Auto-Register**: Tool automatically discovered - no manual registration!
5. **Test**: Create `tools/custom/test_your_tool.py` for self-contained testing
6. **Document**: Add to registry section above
7. **Validate**: Run quality checks and integration tests

### MCP Interface Design Best Practices

When developing custom tools, consider the **user experience in Claude Code's MCP interface**:

#### Interface Complexity Guidelines
- **Simple Tools**: Target 6-10 parameters (like Chat: 8 parameters)
- **Workflow Tools**: Target 10-15 parameters (like QuickReview: 12 parameters)
- **Complex Tools**: Keep under 20 parameters to avoid overwhelming users

#### Essential vs Optional Parameters
**Essential Parameters** (always show):
- Core functionality parameters (proposal, prompt, etc.)
- User control parameters (temperature, thinking_mode, focus)
- Required workflow fields (step, findings - if workflow tool)

**Hide from Interface**:
- Internal state tracking (`files_checked`, `relevant_context`, `issues_found`)
- Advanced workflow control (`hypothesis`, `backtrack_from_step`, `confidence`)
- Default behaviors (`use_websearch`, `use_assistant_model`)
- Complex configuration (`model_responses`, `current_model_index`)

#### Field Naming and Descriptions
```python
# Good: Clear, user-friendly descriptions
"proposal": "What to review or validate. Be specific about what you want checked."

# Bad: Technical, implementation-focused descriptions  
"proposal": "Input parameter for workflow step execution context"
```

#### Schema Testing
```bash
# Test parameter count and user-friendliness
python -c "
from tools.custom.your_tool import YourTool
tool = YourTool()
schema = tool.get_input_schema()
print(f'Parameters: {len(schema.get(\"properties\", {}))}')
for param in sorted(schema['properties'].keys()):
    print(f'  - {param}')
"
```

#### MCP Interface Impact
- **19+ parameters**: Overwhelming, hard to use
- **12-15 parameters**: Manageable for complex tools  
- **6-10 parameters**: Optimal for simple tools
- **3-5 parameters**: Ideal for focused utilities

The MCP interface in Claude Code directly impacts user adoption and tool usability.

### Adding a New Custom Tool (Legacy Method)
1. **Design**: Plan tool purpose, parameters, and architecture
2. **Implement**: Create tool file following zen patterns
3. **Register**: Add to `__init__.py` and `server.py` (higher merge conflict risk)
4. **Test**: Add simulator tests and run validation
5. **Document**: Add to registry section above
6. **Validate**: Run quality checks and integration tests

### Maintenance Routine
- **Weekly**: Check for upstream updates and pull if available
- **After Pull**: Run post-pull validation checklist
- **Monthly**: Review model configuration for changes
- **As Needed**: Update custom tools for new model capabilities

---

*This document is maintained to ensure all custom tools remain functional across upstream updates. Update this registry whenever adding new custom tools or modifying existing ones.*