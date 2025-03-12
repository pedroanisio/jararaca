"""
Tests for the Code Quality Chain Pipeline implementation.
"""

import os
import unittest
from unittest.mock import MagicMock, mock_open, patch

from jararaca.chain_pipeline import CodeQualityChainPipeline, main
from jararaca.utils import CheckResult, CheckStatus


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
        with patch(
            "jararaca.pipeline_config.configparser.ConfigParser"
        ) as mock_config, patch(
            "jararaca.pipeline_config.load_config"
        ) as mock_load_config, patch(
            "jararaca.chain_pipeline.CheckChain"
        ) as mock_chain:
            # Create mock instances
            mock_chain_instance = MagicMock()
            mock_chain.return_value = mock_chain_instance

            # Mock config
            mock_config_instance = MagicMock()
            mock_config.return_value = mock_config_instance
            mock_config_instance.sections.return_value = ["general", "paths"]
            mock_config_instance.__getitem__.return_value = {"key": "value"}

            mock_load_config.return_value = {
                "min_test_coverage": "80",
                "max_file_length": "300",
            }

            # Initialize the pipeline
            pipeline = CodeQualityChainPipeline(".")

            # Verify initialization
            self.assertEqual(pipeline.project_path, os.path.abspath("."))
            mock_chain.assert_called_once()

    def test_build_check_chain(self):
        """Test building the check chain."""
        with patch("jararaca.chain_pipeline.CheckChain") as mock_chain, patch(
            "jararaca.chain_pipeline.load_config"
        ) as mock_load_config:
            # Create mock instances
            mock_chain_instance = MagicMock()
            mock_chain.return_value = mock_chain_instance

            mock_load_config.return_value = {
                "min_test_coverage": "80",
                "max_file_length": "300",
            }

            # Initialize the pipeline
            pipeline = CodeQualityChainPipeline(".")

            # Verify the chain was built
            mock_chain.assert_called_once()
            self.assertEqual(
                mock_chain_instance.add_link.call_count, 12
            )  # There are 12 checks in the chain

    def test_run(self):
        """Test running the pipeline."""
        with patch("jararaca.chain_pipeline.CheckChain") as mock_chain_class, patch(
            "jararaca.chain_pipeline.Console"
        ) as mock_console_class, patch(
            "jararaca.pipeline_prerequisites.subprocess.run"
        ) as mock_subprocess_run, patch(
            "jararaca.chain_pipeline.os.path.exists"
        ) as mock_exists, patch(
            "jararaca.chain_pipeline.os.path.isdir"
        ) as mock_isdir, patch(
            "jararaca.chain_pipeline.check_prerequisites"
        ) as mock_check_prerequisites, patch(
            "jararaca.chain_pipeline.print_summary"
        ) as mock_print_summary, patch(
            "jararaca.chain_pipeline.load_config"
        ) as mock_load_config:
            # Create mock instances
            mock_chain = MagicMock()
            mock_chain_class.return_value = mock_chain
            mock_console = MagicMock()
            mock_console_class.return_value = mock_console
            mock_load_config.return_value = {
                "src_dirs": "src,app",
                "min_test_coverage": "80",
            }

            # Set up return values for mockes
            mock_exists.return_value = True
            mock_isdir.return_value = True
            mock_subprocess_run.return_value = MagicMock(returncode=0)

            # Set up the check chain to return results
            mock_results = [
                CheckResult("Test1", CheckStatus.PASSED, "Test passed"),
                CheckResult("Test2", CheckStatus.PASSED, "Test passed"),
            ]
            mock_chain.execute.return_value = mock_results

            # Initialize and run the pipeline
            pipeline = CodeQualityChainPipeline(".")
            result = pipeline.run()

            # Verify the run
            self.assertTrue(result)
            mock_chain.execute.assert_called_once()
            mock_print_summary.assert_called_once()
            self.assertEqual(pipeline.results, mock_results)

    def test_print_summary(self):
        """Test printing the pipeline summary."""
        with patch(
            "jararaca.pipeline_reporting.create_summary_table"
        ) as mock_create_table, patch(
            "jararaca.chain_pipeline.Console"
        ) as mock_console_class, patch(
            "jararaca.chain_pipeline.print_summary"
        ) as mock_print_summary, patch(
            "jararaca.chain_pipeline.load_config"
        ) as mock_load_config, patch(
            "jararaca.chain_pipeline.CheckChain"
        ) as mock_chain_class, patch(
            "jararaca.chain_pipeline.check_prerequisites"
        ) as mock_check_prerequisites, patch(
            "jararaca.chain_pipeline.os.path.exists"
        ) as mock_exists, patch(
            "jararaca.chain_pipeline.os.path.isdir"
        ) as mock_isdir:

            # Set up file system mocks
            mock_exists.return_value = True
            mock_isdir.return_value = True

            # Create mock instances
            mock_chain = MagicMock()
            mock_chain_class.return_value = mock_chain
            mock_console = MagicMock()
            mock_console_class.return_value = mock_console
            mock_table = MagicMock()
            mock_create_table.return_value = mock_table
            mock_load_config.return_value = {
                "min_test_coverage": "80",
                "src_dirs": "src",
            }

            # Set up results
            mock_results = [
                CheckResult("Test1", CheckStatus.PASSED, "Test passed"),
                CheckResult("Test2", CheckStatus.FAILED, "Test failed"),
                CheckResult("Test3", CheckStatus.SKIPPED, "Test skipped"),
            ]

            # Set up the chain to return our mock results
            mock_chain.execute.return_value = mock_results

            # Initialize the pipeline
            pipeline = CodeQualityChainPipeline(".")

            # Run the pipeline to trigger print_summary
            pipeline.run()

            # Verify print_summary was called with the results
            mock_print_summary.assert_called_once_with(mock_console, mock_results)

    @patch("jararaca.chain_pipeline.ArgumentParser")
    @patch("jararaca.chain_pipeline.CodeQualityChainPipeline")
    def test_main_success(self, mock_pipeline_class, mock_arg_parser):
        """Test main function with successful run."""

        # Create mock instances
        mock_args = MagicMock()
        mock_args.project_path = "."
        mock_args.config = None
        mock_args.json_output = None
        mock_args.auto_commit = False

        mock_arg_parser_instance = MagicMock()
        mock_arg_parser.return_value = mock_arg_parser_instance
        mock_arg_parser_instance.parse_args.return_value = mock_args

        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_pipeline.run.return_value = True  # Simulate success

        # Call main
        result = main([".", "--config", "config.ini"])

        # Verify main
        mock_arg_parser_instance.parse_args.assert_called_once()
        mock_pipeline_class.assert_called_once_with(".", None)
        mock_pipeline.run.assert_called_once()
        self.assertEqual(result, 0)  # Success return code

    @patch("jararaca.chain_pipeline.ArgumentParser")
    @patch("jararaca.chain_pipeline.CodeQualityChainPipeline")
    def test_main_failure(self, mock_pipeline_class, mock_arg_parser):
        """Test main function with failed run."""

        # Create mock instances
        mock_args = MagicMock()
        mock_args.project_path = "."
        mock_args.config = None
        mock_args.json_output = None
        mock_args.auto_commit = False

        mock_arg_parser_instance = MagicMock()
        mock_arg_parser.return_value = mock_arg_parser_instance
        mock_arg_parser_instance.parse_args.return_value = mock_args

        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_pipeline.run.return_value = False  # Simulate failure

        # Call main
        result = main([".", "--config", "config.ini"])

        # Verify main
        mock_arg_parser_instance.parse_args.assert_called_once()
        mock_pipeline_class.assert_called_once_with(".", None)
        mock_pipeline.run.assert_called_once()
        self.assertEqual(result, 1)  # Failure return code

    @patch("jararaca.chain_pipeline.ArgumentParser")
    @patch("jararaca.chain_pipeline.CodeQualityChainPipeline")
    def test_main_exception(self, mock_pipeline_class, mock_arg_parser):
        """Test main function with exception."""

        # Create mock instances
        mock_args = MagicMock()
        mock_args.project_path = "."
        mock_args.config = None
        mock_args.json_output = None
        mock_args.auto_commit = False

        mock_arg_parser_instance = MagicMock()
        mock_arg_parser.return_value = mock_arg_parser_instance
        mock_arg_parser_instance.parse_args.return_value = mock_args

        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_pipeline.run.side_effect = Exception(
            "Test exception"
        )  # Simulate exception

        # Call main
        result = main([".", "--config", "config.ini"])

        # Verify main
        mock_arg_parser_instance.parse_args.assert_called_once()
        mock_pipeline_class.assert_called_once_with(".", None)
        mock_pipeline.run.assert_called_once()
        self.assertEqual(result, 2)  # Exception return code

    def test_json_output(self):
        """Test the JSON output functionality."""
        with patch("jararaca.chain_pipeline.CheckChain") as mock_chain_class, patch(
            "jararaca.chain_pipeline.Console"
        ) as mock_console_class, patch(
            "builtins.open", mock_open()
        ) as mock_file, patch(
            "jararaca.chain_pipeline.load_config"
        ) as mock_load_config, patch(
            "jararaca.chain_pipeline.results_to_json"
        ) as mock_results_to_json, patch(
            "jararaca.chain_pipeline.save_json_output"
        ) as mock_save_json_output:
            # Create mock instances
            mock_chain = MagicMock()
            mock_chain_class.return_value = mock_chain
            mock_console = MagicMock()
            mock_console_class.return_value = mock_console
            mock_load_config.return_value = {"min_test_coverage": "80"}

            # Set up the check chain to return results
            mock_results = [
                CheckResult("Test1", CheckStatus.PASSED, "Test passed"),
                CheckResult("Test2", CheckStatus.FAILED, "Test failed"),
            ]
            mock_chain.execute.return_value = mock_results

            # Mock JSON output
            mock_json_output = {"test": "json"}
            mock_results_to_json.return_value = mock_json_output

            # Initialize the pipeline and set results
            pipeline = CodeQualityChainPipeline(".")
            pipeline.results = mock_results

            # Call save_json_output
            pipeline.save_json_output("test.json")

            # Verify save_json_output was called
            mock_results_to_json.assert_called_once_with(
                mock_results, pipeline.project_path, pipeline.config
            )
            mock_save_json_output.assert_called_once_with(
                mock_json_output, "test.json", mock_console
            )
