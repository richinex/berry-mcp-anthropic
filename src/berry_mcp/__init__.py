"""
Berry MCP Server - Universal MCP server framework using Anthropic's official SDK
Create and deploy Model Context Protocol servers with any tools
"""

__version__ = "0.1.0"
__author__ = "Richard Chukwu"
__email__ = "richinex@gmail.com"

# Import Anthropic's official MCP SDK components
from mcp.server.fastmcp import FastMCP

from .server import auto_discover_tools, create_server, run_stdio_server

# Import our custom decorators and utilities
from .tools.decorators import tool

__all__ = [
    "FastMCP",
    "tool",
    "create_server",
    "run_stdio_server",
    "auto_discover_tools",
]
