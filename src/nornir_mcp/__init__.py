"""Nornir MCP - Model Context Protocol server for network automation.

This package provides an MCP server that exposes Nornir network automation
capabilities to LLMs, allowing AI models to interact with network devices
through standardized tools for device discovery, fact gathering, and
configuration management.
"""

# Import main functions to make them available at package level
from .main import main

__version__ = "0.1.0"
__author__ = "Nornir MCP Team"
__all__ = ["main"]