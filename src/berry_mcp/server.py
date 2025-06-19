"""
Main entry point for Berry MCP Server using Anthropic's official MCP SDK with FastMCP
"""

import argparse
import asyncio
import os
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from .utils.logging import setup_logging


def create_server(
    tool_modules: Any = None, server_name: str | None = None, log_level: str = "INFO"
) -> FastMCP:
    """Create FastMCP server with configurable name and auto-discover tools"""
    # Set up logging
    setup_logging(level=log_level, disable_stdio_logging=True)

    # Create server with configurable name
    name = server_name or os.getenv("BERRY_MCP_SERVER_NAME", "berry-mcp-anthropic")
    mcp = FastMCP(name)

    # Load tool modules if specified
    if tool_modules:
        for module in tool_modules:
            # Import the module to trigger tool registration
            auto_discover_tools(module)
    else:
        # Auto-discover from default tools package
        try:
            from . import tools

            auto_discover_tools(tools)
        except ImportError:
            # No default tools package found
            pass

    # Register all collected tools with the FastMCP instance
    from .tools.decorators import register_tools_with_fastmcp

    register_tools_with_fastmcp(mcp)

    return mcp


def run_stdio_server(
    tool_modules: Any = None, server_name: str | None = None, log_level: str = "INFO"
) -> None:
    """Run MCP server with stdio transport using FastMCP"""
    mcp = create_server(tool_modules, server_name, log_level)

    # Run the server (FastMCP.run is synchronous)
    mcp.run(transport="stdio")


def auto_discover_tools(module: Any) -> None:
    """Auto-discover and register tools from a module using FastMCP patterns"""
    import pkgutil

    # FastMCP automatically registers tools when they are decorated and imported.
    # We just need to ensure the modules are imported to trigger tool registration.

    # Import all submodules to trigger tool registration
    if hasattr(module, "__path__"):
        for _, name, _ in pkgutil.iter_modules(module.__path__):
            try:
                submodule_name = f"{module.__name__}.{name}"
                __import__(submodule_name)
            except ImportError as e:
                print(
                    f"Warning: Could not import tool module '{submodule_name}': {e}",
                    file=sys.stderr,
                )


def cli_main() -> None:
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Berry MCP Server - Universal MCP server framework using Anthropic SDK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  BERRY_MCP_SERVER_NAME    Server name identifier
  BERRY_MCP_LOG_LEVEL      Logging level (DEBUG, INFO, WARNING, ERROR)
  BERRY_MCP_TOOLS_PATH     Comma-separated paths to tool modules

Examples:
  # Run with stdio (for VS Code integration)
  berry-mcp

  # With custom tools module
  BERRY_MCP_TOOLS_PATH=my_tools berry-mcp
""",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=os.getenv("BERRY_MCP_LOG_LEVEL", "INFO"),
        help="Logging level (default: INFO, env: BERRY_MCP_LOG_LEVEL)",
    )
    parser.add_argument(
        "--server-name",
        default=os.getenv("BERRY_MCP_SERVER_NAME"),
        help="Server name identifier (env: BERRY_MCP_SERVER_NAME)",
    )
    parser.add_argument(
        "--tools-path",
        default=os.getenv("BERRY_MCP_TOOLS_PATH"),
        help="Comma-separated paths to tool modules (env: BERRY_MCP_TOOLS_PATH)",
    )

    args = parser.parse_args()

    # Load custom tool modules if specified
    tool_modules = None
    if args.tools_path:
        import importlib

        tool_modules = []
        for path in args.tools_path.split(","):
            path = path.strip()
            if path:
                try:
                    module = importlib.import_module(path)
                    tool_modules.append(module)
                except ImportError as e:
                    print(
                        f"Warning: Could not import tool module '{path}': {e}",
                        file=sys.stderr,
                    )

    try:
        # FastMCP.run() is synchronous and handles its own event loop
        run_stdio_server(
            tool_modules=tool_modules,
            server_name=args.server_name,
            log_level=args.log_level,
        )
    except KeyboardInterrupt:
        print("Server stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


# For backwards compatibility
def main() -> None:
    """Main entry point (backwards compatibility)"""
    run_stdio_server()


if __name__ == "__main__":
    cli_main()
