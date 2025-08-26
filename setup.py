#!/usr/bin/env python
"""Setup script for circuit-sim package."""

from setuptools import setup, find_packages

# Setup is now mostly handled by pyproject.toml
# This file exists for compatibility
setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
