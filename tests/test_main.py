"""
Tests for the main entry point of the code quality pipeline.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from code_quality.pipeline import main


class TestMain(unittest.TestCase):
    """Test cases for the main function."""

    @patch("code_quality.pipeline.CodeQualityPipeline")
    @patch("code_quality.pipeline.argparse.ArgumentParser.parse_args")
    def test_main_simple(self, mock_parse_args, mock_pipeline_class):
        """Test the main function with basic arguments."""
        # Mock the parsed arguments
        mock_parse_args.return_value = MagicMock(
            project_path="/fake/path", config=None, auto_commit=False
        )

        # Mock the pipeline object
        mock_pipeline = MagicMock()
        mock_pipeline.run_all_checks.return_value = True
        mock_pipeline_class.return_value = mock_pipeline

        # Mock sys.exit to prevent actual exit
        with patch("sys.exit") as mock_exit:
            main()

            # Verify the pipeline was created with the correct path
            mock_pipeline_class.assert_called_once_with("/fake/path", None)

            # Verify run_all_checks was called
            mock_pipeline.run_all_checks.assert_called_once()

            # Verify process_branch_and_commit was called
            mock_pipeline.process_branch_and_commit.assert_called_once()

            # Verify system exit with success code
            mock_exit.assert_called_once_with(0)

    @patch("code_quality.pipeline.CodeQualityPipeline")
    @patch("code_quality.pipeline.argparse.ArgumentParser.parse_args")
    def test_main_with_config(self, mock_parse_args, mock_pipeline_class):
        """Test the main function with a custom config file."""
        # Mock the parsed arguments
        mock_parse_args.return_value = MagicMock(
            project_path="/fake/path", config="/fake/config.ini", auto_commit=False
        )

        # Mock the pipeline object
        mock_pipeline = MagicMock()
        mock_pipeline.run_all_checks.return_value = True
        mock_pipeline_class.return_value = mock_pipeline

        # Mock sys.exit to prevent actual exit
        with patch("sys.exit") as mock_exit:
            main()

            # Verify the pipeline was created with the config file
            mock_pipeline_class.assert_called_once_with(
                "/fake/path", "/fake/config.ini"
            )

            # Verify system exit with success code
            mock_exit.assert_called_once_with(0)

    @patch("code_quality.pipeline.CodeQualityPipeline")
    @patch("code_quality.pipeline.argparse.ArgumentParser.parse_args")
    def test_main_with_auto_commit(self, mock_parse_args, mock_pipeline_class):
        """Test the main function with auto-commit enabled."""
        # Mock the parsed arguments
        mock_parse_args.return_value = MagicMock(
            project_path="/fake/path", config=None, auto_commit=True
        )

        # Mock the pipeline and config
        mock_pipeline = MagicMock()
        mock_pipeline.run_all_checks.return_value = True
        mock_pipeline.config = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline

        # Mock sys.exit to prevent actual exit
        with patch("sys.exit") as mock_exit:
            main()

            # Verify auto-commit was enabled in the config
            mock_pipeline.config.set.assert_called_once_with(
                "general", "enable_auto_commit", "true"
            )

            # Verify system exit with success code
            mock_exit.assert_called_once_with(0)

    @patch("code_quality.pipeline.CodeQualityPipeline")
    @patch("code_quality.pipeline.argparse.ArgumentParser.parse_args")
    def test_main_with_failed_checks(self, mock_parse_args, mock_pipeline_class):
        """Test the main function when checks fail."""
        # Mock the parsed arguments
        mock_parse_args.return_value = MagicMock(
            project_path="/fake/path", config=None, auto_commit=False
        )

        # Mock the pipeline object with failing checks
        mock_pipeline = MagicMock()
        mock_pipeline.run_all_checks.return_value = False
        mock_pipeline_class.return_value = mock_pipeline

        # Mock sys.exit to prevent actual exit
        with patch("sys.exit") as mock_exit:
            main()

            # Verify process_branch_and_commit was not called
            mock_pipeline.process_branch_and_commit.assert_not_called()

            # Verify system exit with error code
            mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
