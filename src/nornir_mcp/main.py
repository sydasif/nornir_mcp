"""Main entry point for Nornir MCP server.

This module serves as the main entry point for the Nornir MCP server.
The actual implementation is split between:
- nornir_init.py: Handles Nornir initialization and instance management
- mcp_server.py: Contains the MCP server and tool definitions
"""

from .mcp_server import main


if __name__ == "__main__":
    main()
