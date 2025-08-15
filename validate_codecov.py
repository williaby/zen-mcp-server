#!/usr/bin/env python3
"""
Codecov Implementation Validation Script

This script validates that the complete codecov implementation is working correctly
by testing coverage generation for different test types.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, capture_output=True):
    """Run a command and return the result."""
    print(f"🔍 {description}...")
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True, check=False)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)


def validate_codecov_config():
    """Validate codecov.yaml configuration."""
    print("🔧 Validating codecov configuration...")

    codecov_path = Path("codecov.yaml")
    if not codecov_path.exists():
        print("❌ codecov.yaml not found")
        return False

    try:
        import yaml

        with open(codecov_path) as f:
            config = yaml.safe_load(f)

        # Check key components
        required_sections = ["codecov", "coverage", "component_management", "flags"]
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing required section: {section}")
                return False

        # Check flags
        expected_flags = ["unit", "integration", "simulator"]
        flags = config.get("flags", {})
        for flag in expected_flags:
            if flag not in flags:
                print(f"❌ Missing flag: {flag}")
                return False
            if not flags[flag].get("carryforward"):
                print(f"❌ Flag {flag} missing carryforward setting")
                return False

        print("✅ codecov.yaml configuration is valid")
        return True

    except Exception as e:
        print(f"❌ Error validating codecov.yaml: {e}")
        return False


def validate_coverage_dependencies():
    """Validate coverage dependencies are installed."""
    print("🔧 Validating coverage dependencies...")

    success, _, _ = run_command("python -c 'import coverage; import pytest_cov'", "Check coverage imports")
    if success:
        print("✅ Coverage dependencies are installed")
        return True
    else:
        print("❌ Coverage dependencies not found")
        return False


def test_unit_coverage():
    """Test unit test coverage generation."""
    print("🧪 Testing unit test coverage generation...")

    # Run a small subset of unit tests with coverage
    cmd = "python -m pytest tests/test_alias_target_restrictions.py::TestAliasTargetRestrictions::test_openai_alias_target_validation_comprehensive -v --cov=. --cov-report=xml:test-coverage-unit.xml --cov-report=term-missing"
    success, stdout, stderr = run_command(cmd, "Run unit tests with coverage")

    if success and Path("test-coverage-unit.xml").exists():
        print("✅ Unit test coverage generation works")
        return True
    else:
        print(f"❌ Unit test coverage failed: {stderr}")
        return False


def test_pyproject_config():
    """Test pyproject.toml coverage configuration."""
    print("🔧 Testing pyproject.toml coverage configuration...")

    try:
        import toml

        with open("pyproject.toml") as f:
            config = toml.load(f)

        # Check coverage configuration
        if "tool" not in config or "coverage" not in config["tool"]:
            print("❌ No coverage configuration in pyproject.toml")
            return False

        coverage_config = config["tool"]["coverage"]
        required_sections = ["run", "report", "xml", "html"]
        for section in required_sections:
            if section not in coverage_config:
                print(f"❌ Missing coverage section: {section}")
                return False

        print("✅ pyproject.toml coverage configuration is valid")
        return True

    except Exception as e:
        print(f"❌ Error validating pyproject.toml: {e}")
        return False


def test_github_actions():
    """Test GitHub Actions workflow configuration."""
    print("🔧 Testing GitHub Actions workflow configuration...")

    test_yml = Path(".github/workflows/test.yml")
    codecov_yml = Path(".github/workflows/codecov.yml")

    if not test_yml.exists():
        print("❌ .github/workflows/test.yml not found")
        return False

    if not codecov_yml.exists():
        print("❌ .github/workflows/codecov.yml not found")
        return False

    # Check test.yml has coverage
    with open(test_yml) as f:
        content = f.read()
        if "--cov=" not in content or "codecov/codecov-action" not in content:
            print("❌ test.yml missing coverage configuration")
            return False

    print("✅ GitHub Actions workflows are configured for coverage")
    return True


def cleanup():
    """Clean up test files."""
    test_files = ["test-coverage-unit.xml", "test-coverage-integration.xml"]
    for file in test_files:
        if Path(file).exists():
            Path(file).unlink()


def main():
    """Main validation function."""
    print("🚀 Codecov Implementation Validation")
    print("=" * 50)

    validations = [
        ("Codecov Configuration", validate_codecov_config),
        ("Coverage Dependencies", validate_coverage_dependencies),
        ("PyProject Configuration", test_pyproject_config),
        ("GitHub Actions Workflows", test_github_actions),
        ("Unit Test Coverage", test_unit_coverage),
    ]

    passed = 0
    total = len(validations)

    for name, validator in validations:
        print(f"\n📋 {name}")
        print("-" * 30)
        try:
            if validator():
                passed += 1
        except Exception as e:
            print(f"❌ Validation failed with exception: {e}")

    print("\n🎯 Validation Summary")
    print("=" * 50)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All codecov validations passed!")
        print("✅ Codecov implementation is complete and functional")
        cleanup()
        return 0
    else:
        print("❌ Some validations failed")
        cleanup()
        return 1


if __name__ == "__main__":
    sys.exit(main())
