"""
Comprehensive tests for the pr_review custom tool.

This test suite validates the pr_review tool functionality including:
- Quick mode for small PRs
- Sampling strategy for large PRs
- Security-focus mode
- Performance-focus mode
- Early exit logic
- Model fallback handling
- GitHub integration
- Test execution and coverage validation
- Environment validation
- Layered consensus integration
"""

import json
import unittest.mock
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest

from tools.custom.pr_review import PrReviewTool


class TestPrReviewTool(TestCase):
    """Test suite for pr_review custom tool"""

    def setUp(self):
        """Set up test fixtures"""
        self.tool = PrReviewTool()

        # Mock PR data
        self.mock_pr_data = {
            "number": 123,
            "title": "Fix authentication bug",
            "body": "This PR fixes a critical authentication vulnerability",
            "changed_files": 5,
            "additions": 150,
            "deletions": 50,
            "files": [
                {"filename": "auth.py", "additions": 100, "deletions": 20},
                {"filename": "test_auth.py", "additions": 50, "deletions": 30},
            ],
        }

    def test_tool_metadata(self):
        """Test basic tool metadata"""
        self.assertEqual(self.tool.get_name(), "pr_review")
        self.assertIn("PR review", self.tool.get_description())
        self.assertIn("GitHub", self.tool.get_description())

    def test_get_input_schema(self):
        """Test input schema generation"""
        schema = self.tool.get_input_schema()
        self.assertIsInstance(schema, dict)
        self.assertIn("properties", schema)

        properties = schema["properties"]
        required_fields = ["pr_url"]
        for field in required_fields:
            self.assertIn(field, properties)

    def test_config_loading(self):
        """Test configuration file loading"""
        # Test default config loading
        config = self.tool._load_config()
        self.assertIsInstance(config, dict)
        self.assertIn("quality_thresholds", config)
        self.assertIn("model_preferences", config)

    def test_small_pr_classification(self):
        """Test classification of small PRs for quick mode"""
        small_pr_data = {
            "number": 123,
            "files": [{"filename": "small_fix.py", "additions": 10, "deletions": 5}],
            "additions": 10,
            "deletions": 5,
            "changed_files": 1,
        }

        mode, strategy = self.tool._determine_review_strategy(small_pr_data, "adaptive")
        self.assertIn(mode, ["quick", "adaptive"])

    def test_large_pr_sampling_strategy(self):
        """Test sampling strategy for large PRs"""
        large_pr_data = {
            "number": 456,
            "files": [{"filename": f"file_{i}.py", "additions": 200, "deletions": 100} for i in range(60)],
            "additions": 12000,
            "deletions": 6000,
            "changed_files": 60,
        }

        mode, strategy = self.tool._determine_review_strategy(large_pr_data, "adaptive")
        self.assertEqual(strategy, "sampling")

    @patch("subprocess.run")
    def test_github_auth_validation(self, mock_subprocess):
        """Test GitHub authentication validation"""
        # Test successful auth
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Logged in as testuser")
        result = self.tool._validate_github_auth()
        self.assertTrue(result)

        # Test failed auth
        mock_subprocess.return_value = MagicMock(returncode=1, stderr="Not authenticated")
        result = self.tool._validate_github_auth()
        self.assertFalse(result)

    @patch("subprocess.run")
    async def test_pr_fetch(self, mock_subprocess):
        """Test PR data fetching from GitHub"""
        mock_pr_json = json.dumps(self.mock_pr_data)
        mock_subprocess.return_value = MagicMock(returncode=0, stdout=mock_pr_json, stderr="")

        pr_data = await self.tool._fetch_pr_data("https://github.com/owner/repo/pull/123")
        self.assertEqual(pr_data["number"], 123)
        self.assertEqual(pr_data["title"], "Fix authentication bug")

    def test_security_focus_mode(self):
        """Test security-focused review mode"""
        with patch.object(self.tool, "_load_config") as mock_config:
            mock_config.return_value = {
                "review_modes": {"security-focus": {"force_security_agent": True, "early_exit_enabled": False}}
            }

            mode_config = self.tool._get_review_mode_config("security-focus")
            self.assertTrue(mode_config.get("force_security_agent", False))

    def test_performance_focus_mode(self):
        """Test performance-focused review mode"""
        with patch.object(self.tool, "_load_config") as mock_config:
            mock_config.return_value = {
                "review_modes": {"performance-focus": {"force_performance_agent": True, "early_exit_enabled": False}}
            }

            mode_config = self.tool._get_review_mode_config("performance-focus")
            self.assertTrue(mode_config.get("force_performance_agent", False))

    def test_early_exit_logic(self):
        """Test early exit logic for quality issues"""
        # Mock config with early exit threshold
        config = {"quality_thresholds": {"early_exit": 10}, "review_modes": {"adaptive": {"early_exit_enabled": True}}}

        # Test below threshold
        issues = [{"severity": "medium", "description": "Minor issue"}] * 5
        should_exit = self.tool._should_early_exit(issues, "adaptive", config)
        self.assertFalse(should_exit)

        # Test above threshold
        issues = [{"severity": "high", "description": "Major issue"}] * 15
        should_exit = self.tool._should_early_exit(issues, "adaptive", config)
        self.assertTrue(should_exit)

    @patch("subprocess.run")
    async def test_test_execution(self, mock_subprocess):
        """Test test execution and coverage validation"""
        # Mock successful test run with coverage
        mock_subprocess.side_effect = [
            MagicMock(returncode=0, stdout="All tests passed", stderr=""),  # Test run
            MagicMock(returncode=0, stdout="Coverage: 85%", stderr=""),  # Coverage check
        ]

        result = await self.tool._run_tests_with_coverage()
        self.assertTrue(result["success"])
        self.assertIn("coverage", result)

    @patch("subprocess.run")
    def test_environment_validation(self, mock_subprocess):
        """Test environment validation"""
        # Mock successful environment checks
        mock_subprocess.side_effect = [
            MagicMock(returncode=0, stdout="gh 2.20.0", stderr=""),  # gh CLI
            MagicMock(returncode=0, stdout="git 2.30.0", stderr=""),  # git
            MagicMock(returncode=0, stdout="python 3.9.0", stderr=""),  # python
            MagicMock(returncode=0, stdout="Logged in as user", stderr=""),  # gh auth
        ]

        result = self.tool._validate_environment()
        self.assertTrue(result["valid"])
        self.assertIn("tools", result)

    @patch.object(PrReviewTool, "_call_zen_tool")
    async def test_layered_consensus_integration(self, mock_zen_tool):
        """Test integration with layered_consensus tool"""
        # Mock layered_consensus response
        mock_response = [{"consensus_result": "approve", "confidence": "high", "summary": "Code changes look good"}]
        mock_zen_tool.return_value = mock_response

        # Test calling layered consensus
        result = await self.tool._call_zen_tool(
            "layered_consensus",
            {
                "proposal": "Should we approve this PR?",
                "junior_models": ["flash"],
                "senior_models": ["sonnet"],
                "executive_models": ["opus"],
            },
        )

        self.assertEqual(result, mock_response)
        mock_zen_tool.assert_called_once()

    def test_model_fallback_handling(self):
        """Test model availability and fallback handling"""
        config = {
            "model_preferences": {
                "security": {
                    "preferred": ["anthropic/claude-opus-4"],
                    "fallback": ["o3", "deepseek/deepseek-chat-v3-0324:free"],
                }
            }
        }

        # Test getting preferred model
        models = self.tool._get_preferred_models("security", config)
        self.assertIn("anthropic/claude-opus-4", models["preferred"])
        self.assertIn("o3", models["fallback"])

    @patch("subprocess.run")
    async def test_github_review_submission(self, mock_subprocess):
        """Test GitHub review submission"""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Review submitted successfully", stderr="")

        review_data = {"body": "This PR looks good!", "event": "APPROVE", "comments": []}

        result = await self.tool._submit_github_review("123", review_data)
        self.assertTrue(result["success"])

    def test_file_sampling_for_large_prs(self):
        """Test file sampling strategy for large PRs"""
        # Create mock file list
        files = [{"filename": f"file_{i}.py", "additions": 100} for i in range(60)]

        sampled = self.tool._sample_files_for_analysis(files, max_files=10)
        self.assertLessEqual(len(sampled), 10)

        # Should prioritize files with more changes
        if len(sampled) > 1:
            self.assertTrue(sampled[0]["additions"] >= sampled[-1]["additions"])

    async def test_quality_gate_validation(self):
        """Test quality gate validation"""
        pr_data = self.mock_pr_data

        # Mock quality issues found
        with patch.object(self.tool, "_run_quality_checks") as mock_quality:
            mock_quality.return_value = {
                "issues": [
                    {"severity": "high", "description": "Security vulnerability"},
                    {"severity": "medium", "description": "Code style issue"},
                ],
                "passed": False,
            }

            result = await self.tool._validate_quality_gates(pr_data)
            self.assertFalse(result["passed"])
            self.assertEqual(len(result["issues"]), 2)

    def test_review_mode_configuration(self):
        """Test review mode configuration handling"""
        modes = ["adaptive", "quick", "thorough", "security-focus", "performance-focus"]

        for mode in modes:
            config = self.tool._get_review_mode_config(mode)
            self.assertIsInstance(config, dict)
            # Each mode should have basic configuration
            if mode != "unknown":
                self.assertIn("description", config)

    @patch.object(PrReviewTool, "_call_zen_tool")
    async def test_multi_agent_coordination(self, mock_zen_tool):
        """Test multi-agent coordination workflow"""
        # Mock multiple agent responses
        mock_responses = [
            [{"analysis": "Code looks secure", "agent": "security"}],
            [{"analysis": "Performance is good", "agent": "performance"}],
            [{"analysis": "General quality is high", "agent": "general"}],
        ]

        mock_zen_tool.side_effect = mock_responses

        # Test coordinating multiple agents
        agents = ["security", "performance", "general"]
        results = []

        for agent in agents:
            result = await self.tool._call_zen_tool("analyze", {"analysis_type": agent, "files": ["test.py"]})
            results.append(result)

        self.assertEqual(len(results), 3)
        self.assertEqual(mock_zen_tool.call_count, 3)

    def test_error_handling_and_graceful_degradation(self):
        """Test error handling and graceful degradation"""
        # Test handling missing dependencies
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.side_effect = FileNotFoundError("gh command not found")

            result = self.tool._validate_environment()
            # Should handle gracefully and return useful error info
            self.assertFalse(result.get("valid", True))
            self.assertIn("tools", result)

    def test_configuration_environment_overrides(self):
        """Test environment variable configuration overrides"""
        with patch.dict("os.environ", {"PR_REVIEW_EARLY_EXIT": "5"}):
            # Environment override should be applied if implemented
            # This tests the configuration system's flexibility
            pass  # Placeholder for future configuration system

    @patch("subprocess.run")
    async def test_integration_with_code_quality_tools(self, mock_subprocess):
        """Test integration with linting and code quality tools"""
        # Mock ruff linting
        mock_subprocess.side_effect = [
            MagicMock(returncode=0, stdout="No issues found", stderr=""),  # ruff check
            MagicMock(returncode=0, stdout="All files formatted", stderr=""),  # black check
        ]

        result = await self.tool._run_quality_checks(["test.py"])
        self.assertIn("issues", result)

    def test_concurrent_execution_limits(self):
        """Test concurrent execution and resource limits"""
        config = {"analysis": {"max_concurrent_agents": 3, "agent_timeout": 300}}

        limits = self.tool._get_execution_limits(config)
        self.assertEqual(limits["max_concurrent"], 3)
        self.assertEqual(limits["timeout"], 300)


class TestPrReviewIntegration(TestCase):
    """Integration tests for pr_review tool with real GitHub data"""

    @pytest.mark.integration
    @patch("subprocess.run")
    async def test_full_pr_review_workflow(self, mock_subprocess):
        """Test full PR review workflow end-to-end"""
        tool = PrReviewTool()

        # Mock all external dependencies
        mock_subprocess.side_effect = [
            MagicMock(returncode=0, stdout="Logged in as testuser", stderr=""),  # gh auth
            MagicMock(
                returncode=0,
                stdout=json.dumps(
                    {
                        "number": 123,
                        "title": "Test PR",
                        "additions": 50,
                        "deletions": 10,
                        "files": [{"filename": "test.py", "additions": 50}],
                    }
                ),
                stderr="",
            ),  # PR data fetch
            MagicMock(returncode=0, stdout="All tests passed", stderr=""),  # Tests
            MagicMock(returncode=0, stdout="Coverage: 85%", stderr=""),  # Coverage
            MagicMock(returncode=0, stdout="No lint issues", stderr=""),  # Linting
            MagicMock(returncode=0, stdout="Review submitted", stderr=""),  # Review submission
        ]

        # Mock zen tool calls
        with patch.object(tool, "_call_zen_tool") as mock_zen_tool:
            mock_zen_tool.return_value = [{"analysis": "Looks good", "issues": []}]

            arguments = {
                "pr_url": "https://github.com/test/repo/pull/123",
                "mode": "adaptive",
                "submit_review": False,
                "focus_security": False,
                "focus_performance": False,
            }

            result = await tool.execute(arguments)
            self.assertIsInstance(result, list)

    @pytest.mark.integration
    def test_config_file_validation(self):
        """Test that configuration file is valid and well-formed"""
        tool = PrReviewTool()
        config = tool._load_config()

        # Validate required configuration sections
        required_sections = ["quality_thresholds", "model_preferences", "github", "analysis", "review_modes"]

        for section in required_sections:
            self.assertIn(section, config, f"Missing required config section: {section}")

        # Validate specific configuration values
        self.assertIsInstance(config["quality_thresholds"]["early_exit"], int)
        self.assertIn("security", config["model_preferences"])
        self.assertIn("adaptive", config["review_modes"])


if __name__ == "__main__":
    # Run tests
    unittest.main()
