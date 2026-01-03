"""Nornir Model Context Protocol (MCP) server for network automation.

This package provides a Model Context Protocol implementation that exposes
Nornir network automation capabilities to LLMs, allowing AI models to
interact with network devices through standardized tools for device
discovery, fact gathering, and configuration management.
"""

from .main import main

__version__ = "0.1.0"
__author__ = "Syed Asif"
__all__ = ["main"]
