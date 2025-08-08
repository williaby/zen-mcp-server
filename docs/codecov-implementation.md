# Codecov Implementation Guide

This document provides a comprehensive overview of the codecov implementation for the Zen MCP Server project, adapted from the successful PromptCraft repository structure.

## Implementation Summary

The codecov implementation provides multi-flag coverage tracking with intelligent carryforward functionality, component-based coverage analysis, and comprehensive GitHub Actions integration.

### Key Features

- **Multi-Flag Architecture**: Separate tracking for unit, integration, and simulator tests
- **Component-Based Analysis**: Coverage organized by MCP server architecture components
- **Carryforward Intelligence**: Prevents false coverage drops when only subset of tests run
- **Cost-Conscious Design**: Free local models for integration, API keys only for simulator tests
- **Development-Friendly**: Local coverage reports and enhanced quality checks

## File Structure

```
.
├── codecov.yaml                          # Main codecov configuration
├── .github/workflows/
│   ├── test.yml                         # Enhanced with coverage uploads
│   └── codecov.yml                      # Comprehensive coverage workflow
├── pyproject.toml                       # Coverage tool configuration
├── requirements-dev.txt                 # Coverage dependencies
├── code_quality_checks.sh               # Enhanced with coverage reporting
├── validate_codecov.py                  # Implementation validation script
└── docs/codecov-implementation.md       # This documentation
```

## Configuration Details

### 1. Codecov Configuration (`codecov.yaml`)

**Key Adaptations from PromptCraft:**
- Lower patch coverage target (80% vs 85%) due to MCP complexity
- Higher threshold allowance (2-3% vs 1-2%) for API-dependent code
- MCP-specific ignores (simulator files, logs, scripts)
- 3-build wait for unit + integration + simulator test uploads

**Flag Definitions:**
```yaml
flags:
  unit:
    paths: ["."]
    carryforward: true    # Critical for intelligent merging
  integration:
    paths: ["."]
    carryforward: true
  simulator:
    paths: ["."]
    carryforward: true
```

**Component Management:**
- `mcp_tools`: Core and custom tools
- `providers`: AI provider integrations  
- `utils`: Shared utility modules
- `server_core`: Main server logic
- `systemprompts`: System prompt definitions
- `configuration`: Config management

### 2. GitHub Actions Integration

**test.yml Enhancements:**
- Added coverage generation to existing unit tests
- Uploads coverage with `unit` flag
- Matrix strategy across Python 3.10-3.12

**codecov.yml Workflow:**
- Separate jobs for unit, integration, simulator tests
- Integration tests use free local Ollama models
- Simulator tests use quick mode for cost efficiency
- Secret management for API keys

### 3. Local Development Support

**Enhanced code_quality_checks.sh:**
```bash
# Now includes coverage reporting
python -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html
```

**pyproject.toml Configuration:**
- Complete coverage configuration
- Excludes test files, logs, scripts from coverage
- HTML and XML report generation
- Branch coverage enabled

## Usage Instructions

### Local Development

1. **Run quality checks with coverage:**
   ```bash
   ./code_quality_checks.sh
   ```

2. **Generate detailed coverage report:**
   ```bash
   source .zen_venv/bin/activate
   python -m pytest tests/ --cov=. --cov-report=html
   open htmlcov/index.html
   ```

3. **Test specific coverage flags:**
   ```bash
   # Unit tests only
   python -m pytest tests/ -m "not integration" --cov=. --cov-report=xml:coverage-unit.xml
   
   # Integration tests (requires Ollama)
   export CUSTOM_API_URL="http://localhost:11434"
   python -m pytest tests/ -m "integration" --cov=. --cov-report=xml:coverage-integration.xml
   ```

### CI/CD Integration

The GitHub Actions workflows automatically:
1. Run unit tests with coverage across Python versions
2. Run integration tests with local Ollama (when available)
3. Run simulator tests in quick mode
4. Upload coverage reports with appropriate flags
5. Combine results using carryforward functionality

### Validation

Run the validation script to ensure everything works:
```bash
python validate_codecov.py
```

This validates:
- ✅ Codecov configuration structure
- ✅ Coverage dependencies installation
- ✅ PyProject configuration validity
- ✅ GitHub Actions workflow setup
- ✅ Unit test coverage generation

## Coverage Targets

### Current Baseline
- **Overall Coverage**: 38% (baseline from initial implementation)
- **Target Coverage**: 80% for new patches
- **Threshold**: 2-3% drop allowed (accounts for MCP complexity)

### Component Expectations
- **MCP Tools**: High coverage priority (user-facing functionality)
- **Providers**: Medium coverage (API integration complexity)
- **Utils**: High coverage (shared functionality)
- **Server Core**: Medium coverage (startup/configuration logic)

## Carryforward Strategy

The carryforward feature is critical for MCP development:
- **Unit tests** always run (fast, no external dependencies)
- **Integration tests** run when Ollama available (free local models)
- **Simulator tests** run selectively (cost-conscious API usage)

When only unit tests run on a PR, integration and simulator coverage are carried forward from the base branch, preventing false coverage drops.

## Best Practices

### For Developers

1. **Always run quality checks** before committing
2. **Check HTML coverage reports** for detailed analysis
3. **Focus on component coverage** rather than overall percentage
4. **Add tests for new MCP tools** (highest priority)

### For CI/CD

1. **Unit tests run everywhere** (GitHub Actions, local development)
2. **Integration tests run when possible** (Ollama available)
3. **Simulator tests run selectively** (API budget considerations)
4. **Coverage reports upload to Codecov** with appropriate flags

## Troubleshooting

### Common Issues

1. **No coverage data collected**
   - Ensure virtual environment is activated
   - Check that coverage dependencies are installed
   - Verify test files are being executed

2. **Coverage reports not uploading**
   - Check CODECOV_TOKEN is set in GitHub secrets
   - Verify XML report files are generated
   - Confirm GitHub Actions workflow syntax

3. **Carryforward not working**
   - Ensure all flags have `carryforward: true`
   - Check that base branch has coverage data
   - Verify flag names match across workflows

### Validation Commands

```bash
# Validate codecov configuration
python validate_codecov.py

# Check coverage configuration syntax
coverage --help

# Test coverage generation
python -m pytest tests/test_quickreview_tool.py --cov=tools.custom.quickreview --cov-report=term-missing
```

## Future Enhancements

1. **Coverage Badges**: Add codecov badges to README
2. **Component Thresholds**: Set specific coverage targets per component
3. **Integration with PRs**: Enhanced PR coverage comments
4. **Performance Tracking**: Monitor coverage trends over time
5. **Advanced Reporting**: Custom coverage analysis for MCP tools

## Summary

This codecov implementation provides comprehensive coverage tracking while being cost-conscious and development-friendly. It adapts the proven PromptCraft approach for the unique needs of MCP tool development, ensuring adequate testing coverage without breaking development workflows or budget constraints.

The multi-flag architecture with carryforward functionality ensures accurate coverage reporting even when only subset of tests run, while the component-based analysis provides meaningful insights into the coverage of different parts of the MCP server architecture.