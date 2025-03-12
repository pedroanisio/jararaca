"""
Tests for the main entry point of the code quality pipeline.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from jararaca.chain_pipeline import main


class TestMain(unittest.TestCase):
    """Test cases for the main function."""

    @patch("jararaca.chain_pipeline.CodeQualityChainPipeline")
    @patch("jararaca.chain_pipeline.ArgumentParser")
    def test_main_simple(self, mock_parser_class, mock_pipeline_class):
        """Test the main function with basic arguments."""
        # Mock the argument parser
        mock_parser = MagicMock()
        mock_parse_args = MagicMock()
        mock_parse_args.project_path = "/fake/path"
        mock_parse_args.config = None
        mock_parse_args.auto_commit = False
        mock_parser.parse_args.return_value = mock_parse_args
        mock_parser_class.return_value = mock_parser

        # Mock the pipeline object
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = True
        mock_pipeline_class.return_value = mock_pipeline

        # Run the main function
        result = main()

        # Verify the pipeline was created with the correct path
        mock_pipeline_class.assert_called_once_with("/fake/path", None)

        # Verify run was called
        mock_pipeline.run.assert_called_once()

        # Verify the correct exit code was returned
        self.assertEqual(result, 0)

    @patch("jararaca.chain_pipeline.CodeQualityChainPipeline")
    @patch("jararaca.chain_pipeline.ArgumentParser")
    def test_main_with_config(self, mock_parser_class, mock_pipeline_class):
        """Test the main function with a custom config file."""
        # Mock the argument parser
        mock_parser = MagicMock()
        mock_parse_args = MagicMock()
        mock_parse_args.project_path = "/fake/path"
        mock_parse_args.config = "/fake/config.ini"
        mock_parse_args.auto_commit = False
        mock_parser.parse_args.return_value = mock_parse_args
        mock_parser_class.return_value = mock_parser

        # Mock the pipeline object
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = True
        mock_pipeline_class.return_value = mock_pipeline

        # Run the main function
        result = main()

        # Verify the pipeline was created with the config file
        mock_pipeline_class.assert_called_once_with("/fake/path", "/fake/config.ini")

        # Verify the correct exit code was returned
        self.assertEqual(result, 0)

    @patch("jararaca.chain_pipeline.CodeQualityChainPipeline")
    @patch("jararaca.chain_pipeline.ArgumentParser")
    def test_main_with_auto_commit(self, mock_parser_class, mock_pipeline_class):
        """Test the main function with auto-commit enabled."""
        # Mock the argument parser
        mock_parser = MagicMock()
        mock_parse_args = MagicMock()
        mock_parse_args.project_path = "/fake/path"
        mock_parse_args.config = None
        mock_parse_args.auto_commit = True
        mock_parser.parse_args.return_value = mock_parse_args
        mock_parser_class.return_value = mock_parser

        # Mock the pipeline and config
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = True
        mock_pipeline.config = {}
        mock_pipeline_class.return_value = mock_pipeline

        # Run the main function
        result = main()

        # Verify auto-commit was enabled in the config
        self.assertEqual(mock_pipeline.config["enable_auto_commit"], "true")

        # Verify the correct exit code was returned
        self.assertEqual(result, 0)

    @patch("jararaca.chain_pipeline.CodeQualityChainPipeline")
    @patch("jararaca.chain_pipeline.ArgumentParser")
    def test_main_with_failed_checks(self, mock_parser_class, mock_pipeline_class):
        """Test the main function when checks fail."""
        # Mock the argument parser
        mock_parser = MagicMock()
        mock_parse_args = MagicMock()
        mock_parse_args.project_path = "/fake/path"
        mock_parse_args.config = None
        mock_parse_args.auto_commit = False
        mock_parser.parse_args.return_value = mock_parse_args
        mock_parser_class.return_value = mock_parser

        # Mock the pipeline object with failing checks
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = False
        mock_pipeline_class.return_value = mock_pipeline

        # Run the main function
        result = main()

        # Verify the correct exit code was returned
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
