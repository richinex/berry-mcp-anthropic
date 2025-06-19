"""
Tests for MCP server using Anthropic FastMCP SDK
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from berry_mcp.server import auto_discover_tools, create_server, run_stdio_server
from berry_mcp.tools.decorators import tool


def test_auto_discover_tools():
    """Test auto-discovery of tools from modules"""

    # Create a mock module without __path__ (should not crash)
    class MockModuleNoPath:
        __name__ = "test_module"

    mock_module = MockModuleNoPath()

    # Test that auto_discover_tools doesn't crash with module without __path__
    auto_discover_tools(mock_module)  # Should not raise exception

    # Test with a module that has __path__ but empty
    class MockModuleWithPath:
        __name__ = "test_module_with_path"
        __path__ = []

    mock_module_with_path = MockModuleWithPath()
    auto_discover_tools(mock_module_with_path)  # Should not raise exception


def test_create_server():
    """Test FastMCP server creation"""
    with patch("berry_mcp.server.FastMCP") as mock_fastmcp_class:
        with patch(
            "berry_mcp.tools.decorators.register_tools_with_fastmcp"
        ) as mock_register:
            with patch("berry_mcp.server.auto_discover_tools"):
                # Mock the FastMCP instance
                mock_server = MagicMock()
                mock_fastmcp_class.return_value = mock_server

                # Test server creation
                server = create_server(server_name="test", log_level="INFO")

                # Verify server was created correctly
                mock_fastmcp_class.assert_called_once_with("test")
                mock_register.assert_called_once_with(mock_server)
                assert server == mock_server


@pytest.mark.asyncio
async def test_run_stdio_server_basic():
    """Test basic stdio server startup"""
    with patch("berry_mcp.server.create_server") as mock_create:
        # Mock the FastMCP instance
        mock_server = AsyncMock()
        mock_server.run = AsyncMock()
        mock_create.return_value = mock_server

        # Should not raise exception
        await run_stdio_server(server_name="test", log_level="INFO")

        # Verify server was created and run was called
        mock_create.assert_called_once_with(None, "test", "INFO")
        mock_server.run.assert_called_once_with(transport="stdio")


@pytest.mark.asyncio
async def test_run_stdio_server_with_tool_modules():
    """Test stdio server with custom tool modules"""

    # Create a mock tool module
    class MockToolModule:
        __name__ = "mock_tools"
        __path__ = ["/mock/path"]

    mock_module = MockToolModule()

    with patch("berry_mcp.server.create_server") as mock_create:
        # Mock the FastMCP instance
        mock_server = AsyncMock()
        mock_server.run = AsyncMock()
        mock_create.return_value = mock_server

        # Run with custom tool modules
        await run_stdio_server(tool_modules=[mock_module])

        # Verify create_server was called with modules
        mock_create.assert_called_once_with([mock_module], None, "INFO")


def test_tool_decorator_integration():
    """Test that our tool decorator works for integration"""

    @tool(description="Test integration tool")
    def test_integration_func(value: str) -> str:
        """Test function for integration"""
        return value.upper()

    # Should have Berry MCP metadata
    assert hasattr(test_integration_func, "_berry_mcp_metadata")
    metadata = test_integration_func._berry_mcp_metadata
    assert metadata["custom_name"] == "test_integration_func"
    assert metadata["custom_description"] == "Test integration tool"

    # Function should still be callable
    result = test_integration_func("hello")
    assert result == "HELLO"


@pytest.mark.asyncio
async def test_run_stdio_server_default_tools():
    """Test stdio server with default tools discovery"""
    with patch("berry_mcp.server.create_server") as mock_create:
        # Mock the FastMCP instance
        mock_server = AsyncMock()
        mock_server.run = AsyncMock()
        mock_create.return_value = mock_server

        # Run without custom tool modules (should use defaults)
        await run_stdio_server()

        # Should have called create_server with defaults
        mock_create.assert_called_once_with(None, None, "INFO")


def test_server_environment_variables():
    """Test server respects environment variables"""
    import os

    # Test default server name from environment
    old_name = os.environ.get("BERRY_MCP_SERVER_NAME")
    try:
        os.environ["BERRY_MCP_SERVER_NAME"] = "env-test-server"

        with patch("berry_mcp.server.FastMCP") as mock_fastmcp_class:
            with patch("berry_mcp.tools.decorators.register_tools_with_fastmcp"):
                # Mock the FastMCP instance
                mock_server = MagicMock()
                mock_fastmcp_class.return_value = mock_server

                # Create server without explicit name (should use env var)
                create_server()

                # Should use environment variable
                mock_fastmcp_class.assert_called_once_with("env-test-server")

    finally:
        # Restore original value
        if old_name is not None:
            os.environ["BERRY_MCP_SERVER_NAME"] = old_name
        elif "BERRY_MCP_SERVER_NAME" in os.environ:
            del os.environ["BERRY_MCP_SERVER_NAME"]
