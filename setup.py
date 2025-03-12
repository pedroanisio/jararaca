#!/usr/bin/env python3
"""
Setup script for the jararaca code quality package.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jararaca",
    version="0.1.0",
    author="Jararaca Team",
    author_email="team@example.com",
    description="A comprehensive Python code quality validation tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jararaca/jararaca",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pytest",
        "black",
        "isort",
        "flake8",
        "mypy",
        "coverage",
        "bandit",
        "ruff",
        "pip-audit",
    ],
    entry_points={
        "console_scripts": [
            "code-quality=jararaca.chain_pipeline:main",
        ],
    },
)
