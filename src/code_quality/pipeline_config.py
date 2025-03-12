"""
Configuration handling for the code quality pipeline.

This module contains utilities for loading and managing pipeline configuration.
"""

import configparser
import logging
import os
from typing import Any, Dict, Optional


def load_config(config_file: Optional[str]) -> Dict[str, Any]:
    """
    Load configuration from file or use defaults.

    Args:
        config_file: Path to the configuration file

    Returns:
        A dictionary containing the configuration
    """
    logging.info("Loading configuration.")
    config_parser = configparser.ConfigParser()

    # Default configuration
    config_parser["general"] = {
        "min_test_coverage": "80",
        "max_file_length": "300",
        "max_function_length": "50",
        "check_bandit": "true",
        "check_mypy": "true",
        "check_ruff": "true",
        "main_branch": "main",
        "enable_auto_commit": "false",
    }
    config_parser["paths"] = {
        "src_dirs": "src,app",
        "test_dir": "tests",
        "exclude_dirs": "venv,.venv,__pycache__,build,dist",
    }

    if config_file and os.path.exists(config_file):
        config_parser.read(config_file)
        logging.info(f"Configuration loaded from {config_file}.")
    else:
        logging.info("Using default configuration.")

    # Convert config to dictionary
    config = {}
    for section in config_parser.sections():
        for key, value in config_parser[section].items():
            config[key] = value

    return config 