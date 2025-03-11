"""
Tests for the Code Quality Chain Pipeline implementation.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from src.code_quality.chain import CheckChain
from src.code_quality.chain_pipeline import CodeQualityChainPipeline, main
from src.code_quality.utils import CheckResult, CheckStatus


class TestCodeQualityChainPipeline(unittest.TestCase):
    """Test cases for the CodeQualityChainPipeline class."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_path = os.path.abspath(os.path.dirname(__file__))

    def tearDown(self):
        """Tear down test fixtures."""
        pass

    def test_initialization(self):
        """Test initializing the pipeline."""
        with patch("src.code_quality.chain_pipeline.CheckChain") as mock_chain, patch(
            "src.code_quality.chain_pipeline.configparser.ConfigParser"
        ) as mock_config:
            # Create mock instances
            mock_chain_instance = MagicMock()
            mock_chain.return_value = mock_chain_instance

            # Mock config
            mock_config_instance = MagicMock()
            mock_config.return_value = mock_config_instance
            mock_config_instance.sections.return_value = ["general", "paths"]
            mock_config_instance.__getitem__.return_value = {"key": "value"}

            # Initialize the pipeline
            pipeline = CodeQualityChainPipeline(self.project_path)

            # Check that the project path is correctly set
            self.assertEqual(pipeline.project_path, self.project_path)

            # Check that the results list is initially empty
            self.assertEqual(pipeline.results, [])

            # Check that build_check_chain was called
            mock_chain.assert_called_once()

    def test_build_check_chain(self):
        """Test building the check chain."""
        with patch(
            "src.code_quality.chain_pipeline.FormattingCheck"
        ) as mock_formatting, patch(
            "src.code_quality.chain_pipeline.ImportsCheck"
        ) as mock_imports, patch(
            "src.code_quality.chain_pipeline.LintingCheck"
        ) as mock_linting, patch(
            "src.code_quality.chain_pipeline.RuffCheck"
        ) as mock_ruff, patch(
            "src.code_quality.chain_pipeline.TypeCheckingLink"
        ) as mock_type, patch(
            "src.code_quality.chain_pipeline.SecurityCheckLink"
        ) as mock_security, patch(
            "src.code_quality.chain_pipeline.TestCoverageCheck"
        ) as mock_coverage, patch(
            "src.code_quality.chain_pipeline.NamingConventionsCheck"
        ) as mock_naming, patch(
            "src.code_quality.chain_pipeline.FileLengthCheck"
        ) as mock_file_length, patch(
            "src.code_quality.chain_pipeline.FunctionLengthCheck"
        ) as mock_func_length, patch(
            "src.code_quality.chain_pipeline.DocstringCheck"
        ) as mock_docstring, patch(
            "src.code_quality.chain_pipeline.DependencyCheck"
        ) as mock_dependency, patch(
            "src.code_quality.chain_pipeline.CheckChain"
        ) as mock_chain_class:

            # Create mock chain
            mock_chain = MagicMock()
            mock_chain_class.return_value = mock_chain

            # Create mock instances for all check classes
            mock_formatting_instance = MagicMock()
            mock_imports_instance = MagicMock()
            mock_linting_instance = MagicMock()
            mock_ruff_instance = MagicMock()
            mock_type_instance = MagicMock()
            mock_security_instance = MagicMock()
            mock_coverage_instance = MagicMock()
            mock_naming_instance = MagicMock()
            mock_file_length_instance = MagicMock()
            mock_func_length_instance = MagicMock()
            mock_docstring_instance = MagicMock()
            mock_dependency_instance = MagicMock()

            # Set up the return values for the mocks
            mock_formatting.return_value = mock_formatting_instance
            mock_imports.return_value = mock_imports_instance
            mock_linting.return_value = mock_linting_instance
            mock_ruff.return_value = mock_ruff_instance
            mock_type.return_value = mock_type_instance
            mock_security.return_value = mock_security_instance
            mock_coverage.return_value = mock_coverage_instance
            mock_naming.return_value = mock_naming_instance
            mock_file_length.return_value = mock_file_length_instance
            mock_func_length.return_value = mock_func_length_instance
            mock_docstring.return_value = mock_docstring_instance
            mock_dependency.return_value = mock_dependency_instance

            # Initialize the pipeline
            pipeline = CodeQualityChainPipeline(self.project_path)

            # Check that all check classes were instantiated
            mock_formatting.assert_called_once()
            mock_imports.assert_called_once()
            mock_linting.assert_called_once()
            mock_ruff.assert_called_once()
            mock_type.assert_called_once()
            mock_security.assert_called_once()
            mock_coverage.assert_called_once()
            mock_naming.assert_called_once()
            mock_file_length.assert_called_once()
            mock_func_length.assert_called_once()
            mock_docstring.assert_called_once()
            mock_dependency.assert_called_once()

            # Check that add_link was called for each check
            self.assertEqual(mock_chain.add_link.call_count, 12)

    def test_run(self):
        """Test running the pipeline."""
        with patch(
            "src.code_quality.chain_pipeline.CheckChain"
        ) as mock_chain_class, patch(
            "src.code_quality.chain_pipeline.Console"
        ) as mock_console_class, patch(
            "src.code_quality.chain_pipeline.subprocess.run"
        ) as mock_subprocess_run:

            # Mock subprocess run for _check_prerequisites
            mock_subprocess_run.return_value.returncode = 0

            # Create mock instances
            mock_chain = MagicMock()
            mock_console = MagicMock()

            mock_chain_class.return_value = mock_chain
            mock_console_class.return_value = mock_console

            # Create mock check results
            mock_results = [
                CheckResult("Test 1", CheckStatus.PASSED, "Test 1 passed"),
                CheckResult("Test 2", CheckStatus.FAILED, "Test 2 failed"),
                CheckResult("Test 3", CheckStatus.SKIPPED, "Test 3 skipped"),
            ]

            # Set up the mock chain to return the mock results
            mock_chain.execute.return_value = mock_results

            # Initialize and run the pipeline
            pipeline = CodeQualityChainPipeline(self.project_path)

            # Override config for test
            pipeline.config = {"src_dirs": "src,app"}

            result = pipeline.run()

            # Check that the chain was executed with the correct context
            mock_chain.execute.assert_called_once()
            context_arg = mock_chain.execute.call_args[0][0]
            self.assertEqual(context_arg["project_path"], self.project_path)
            self.assertEqual(context_arg["source_dirs"], ["src", "app"])

            # Check that the results were set correctly
            self.assertEqual(pipeline.results, mock_results)

            # Check that the result was False (since Test 2 failed)
            self.assertFalse(result)

            # Check that print_summary was called by checking that the console printed a table
            console_calls = mock_console.print.call_args_list
            summary_call_found = False
            for call in console_calls:
                if "Pipeline Summary" in str(call):
                    summary_call_found = True
                    break
            self.assertTrue(summary_call_found)

    def test_print_summary(self):
        """Test printing the pipeline summary."""
        with patch(
            "src.code_quality.chain_pipeline.create_summary_table"
        ) as mock_create_table, patch(
            "src.code_quality.chain_pipeline.Console"
        ) as mock_console_class:

            # Create mock instances
            mock_console = MagicMock()
            mock_table = MagicMock()

            mock_console_class.return_value = mock_console
            mock_create_table.return_value = mock_table

            # Create a pipeline with mock results
            pipeline = CodeQualityChainPipeline(self.project_path)
            pipeline.results = [
                CheckResult("Test 1", CheckStatus.PASSED, "Test 1 passed"),
                CheckResult("Test 2", CheckStatus.FAILED, "Test 2 failed"),
                CheckResult("Test 3", CheckStatus.SKIPPED, "Test 3 skipped"),
            ]

            # Call print_summary
            pipeline._print_summary()

            # Check that create_summary_table was called with the correct counts
            mock_create_table.assert_called_once_with(1, 1, 1)

            # Check that the console printed the table
            mock_console.print.assert_any_call("\n      Pipeline Summary      ")
            mock_console.print.assert_any_call(mock_table)

            # Check that the console printed the failure message
            failure_call_found = False
            for call in mock_console.print.call_args_list:
                if "Some quality checks failed" in str(call):
                    failure_call_found = True
                    break
            self.assertTrue(failure_call_found)

    @patch("src.code_quality.chain_pipeline.ArgumentParser")
    @patch("src.code_quality.chain_pipeline.CodeQualityChainPipeline")
    def test_main_success(self, mock_pipeline_class, mock_arg_parser):
        """Test the main function with a successful run."""
        # Create mock instances
        mock_args = MagicMock()
        mock_args.project_path = self.project_path
        mock_args.config = None
        mock_args.auto_commit = False

        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args

        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = True

        mock_arg_parser.return_value = mock_parser
        mock_pipeline_class.return_value = mock_pipeline

        # Call main
        result = main([self.project_path])

        # Check that the parser was created and parse_args was called
        mock_arg_parser.assert_called_once()
        mock_parser.parse_args.assert_called_once_with([self.project_path])

        # Check that the pipeline was created and run was called
        mock_pipeline_class.assert_called_once_with(self.project_path, None)
        mock_pipeline.run.assert_called_once()

        # Check that the result is 0 (success)
        self.assertEqual(result, 0)

    @patch("src.code_quality.chain_pipeline.ArgumentParser")
    @patch("src.code_quality.chain_pipeline.CodeQualityChainPipeline")
    def test_main_failure(self, mock_pipeline_class, mock_arg_parser):
        """Test the main function with a failed run."""
        # Create mock instances
        mock_args = MagicMock()
        mock_args.project_path = self.project_path
        mock_args.config = None
        mock_args.auto_commit = False

        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args

        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = False

        mock_arg_parser.return_value = mock_parser
        mock_pipeline_class.return_value = mock_pipeline

        # Call main
        result = main([self.project_path])

        # Check that the parser was created and parse_args was called
        mock_arg_parser.assert_called_once()
        mock_parser.parse_args.assert_called_once_with([self.project_path])

        # Check that the pipeline was created and run was called
        mock_pipeline_class.assert_called_once_with(self.project_path, None)
        mock_pipeline.run.assert_called_once()

        # Check that the result is 1 (failure)
        self.assertEqual(result, 1)

    @patch("src.code_quality.chain_pipeline.ArgumentParser")
    @patch("src.code_quality.chain_pipeline.CodeQualityChainPipeline")
    def test_main_exception(self, mock_pipeline_class, mock_arg_parser):
        """Test the main function when an exception occurs."""
        # Create mock instances
        mock_args = MagicMock()
        mock_args.project_path = self.project_path
        mock_args.config = None
        mock_args.auto_commit = False

        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args

        mock_pipeline = MagicMock()
        mock_pipeline.run.side_effect = Exception("Test exception")

        mock_arg_parser.return_value = mock_parser
        mock_pipeline_class.return_value = mock_pipeline

        # Call main
        result = main([self.project_path])

        # Check that the parser was created and parse_args was called
        mock_arg_parser.assert_called_once()
        mock_parser.parse_args.assert_called_once_with([self.project_path])

        # Check that the pipeline was created and run was called
        mock_pipeline_class.assert_called_once_with(self.project_path, None)
        mock_pipeline.run.assert_called_once()

        # Check that the result is 1 (failure)
        self.assertEqual(result, 1)
