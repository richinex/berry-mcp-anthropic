"""
Tool registration decorators for Berry MCP Server using Anthropic FastMCP SDK
"""

import inspect
import logging
from collections.abc import Callable
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

# Type variable for preserving function type
F = TypeVar("F", bound=Callable[..., Any])

# Global registry to store tools before FastMCP instance is created
_tool_registry: list[dict[str, Any]] = []


def tool(
    name: str | None = None,
    description: str | None = None,
    examples: list[dict[str, Any]] | None = None,
) -> Callable[[F], F]:
    """
    Decorator to register a function as an MCP tool using FastMCP.

    This decorator stores tool information to be registered later with FastMCP
    when the server instance is created.

    Args:
        name: Optional custom name for the tool. Defaults to function name.
        description: Optional description for the tool. Defaults to function docstring.
        examples: Optional examples (preserved for compatibility)

    Example:
        @tool(description="Calculate the sum of two numbers")
        def add_numbers(a: int, b: int) -> int:
            '''Add two integers together'''
            return a + b

        @tool()
        def read_file(path: str, encoding: str = "utf-8") -> str:
            '''Read content from a file'''
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
    """

    def decorator(func: F) -> F:
        # Get function metadata
        tool_name = name or func.__name__
        tool_description = description or (func.__doc__ or "").strip()

        # Store tool information in global registry
        _tool_registry.append(
            {
                "func": func,
                "name": tool_name,
                "description": tool_description,
                "examples": examples or [],
            }
        )

        # Store metadata on the function for compatibility
        func._berry_mcp_metadata = {"examples": examples or [], "original_name": func.__name__, "custom_name": tool_name, "custom_description": tool_description}

        logger.debug(
            f"Tool registered for FastMCP: {tool_name} "
            f"({'async' if inspect.iscoroutinefunction(func) else 'sync'})"
        )

        return func

    return decorator


def register_tools_with_fastmcp(mcp_instance) -> None:
    """Register all collected tools with a FastMCP instance"""
    for tool_info in _tool_registry:
        # Use FastMCP's tool decorator
        mcp_instance.tool(
            name=tool_info["name"], description=tool_info["description"]
        )(tool_info["func"])

        logger.debug(f"Registered tool {tool_info['name']} with FastMCP")


def get_registered_tools() -> list[dict[str, Any]]:
    """Get all registered tools (for debugging/testing)"""
    return _tool_registry.copy()


__all__ = ["tool", "register_tools_with_fastmcp", "get_registered_tools"]
