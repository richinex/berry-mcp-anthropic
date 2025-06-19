"""
Integration tests for Berry MCP Server using FastMCP
Tests end-to-end functionality focusing on tool registration and server creation
"""

import pytest

from berry_mcp import FastMCP, create_server, tool
from berry_mcp.tools.decorators import get_registered_tools


def test_server_with_tools_integration():
    """Test that server creation includes all default tools"""
    # Clear any existing tools from previous tests
    from berry_mcp.tools.decorators import _tool_registry

    original_tools = len(_tool_registry)

    # Create server which should auto-discover tools
    server = create_server(server_name="integration-test")

    # Verify server was created
    assert server is not None
    assert server.name == "integration-test"

    # Verify tools were registered
    tools = get_registered_tools()
    assert len(tools) >= original_tools  # Should have at least the original tools


def test_custom_tool_registration():
    """Test that custom tools can be registered"""

    @tool(description="Integration test tool")
    def integration_test_tool(value: str) -> str:
        """Test tool for integration testing"""
        return f"Processed: {value}"

    # Verify tool has metadata
    assert hasattr(integration_test_tool, "_berry_mcp_metadata")
    metadata = integration_test_tool._berry_mcp_metadata
    assert metadata["custom_name"] == "integration_test_tool"
    assert metadata["custom_description"] == "Integration test tool"

    # Verify tool is callable
    result = integration_test_tool("test input")
    assert result == "Processed: test input"

    # Verify tool was added to registry
    tools = get_registered_tools()
    tool_names = [t["name"] for t in tools]
    assert "integration_test_tool" in tool_names


def test_async_tool_integration():
    """Test that async tools work correctly"""
    import asyncio

    @tool(description="Async integration test tool")
    async def async_integration_tool(message: str) -> str:
        """Async test tool"""
        await asyncio.sleep(0.001)  # Minimal async work
        return f"Async: {message}"

    # Verify tool has metadata
    assert hasattr(async_integration_tool, "_berry_mcp_metadata")

    # Verify tool is async and callable
    async def test_async():
        result = await async_integration_tool("test")
        assert result == "Async: test"

    # Run the async test
    asyncio.run(test_async())


def test_server_configuration():
    """Test server configuration options"""
    import os

    # Test with environment variable
    old_name = os.environ.get("BERRY_MCP_SERVER_NAME")
    try:
        os.environ["BERRY_MCP_SERVER_NAME"] = "env-configured-server"
        server = create_server()
        assert server.name == "env-configured-server"
    finally:
        if old_name is not None:
            os.environ["BERRY_MCP_SERVER_NAME"] = old_name
        elif "BERRY_MCP_SERVER_NAME" in os.environ:
            del os.environ["BERRY_MCP_SERVER_NAME"]

    # Test with explicit name
    server = create_server(server_name="explicit-name")
    assert server.name == "explicit-name"


def test_default_tools_loaded():
    """Test that default example tools are loaded"""
    create_server()
    tools = get_registered_tools()

    # Should have some default tools from example_tools.py
    tool_names = [t["name"] for t in tools]
    expected_tools = ["add_numbers", "get_system_info", "generate_uuid"]

    for expected_tool in expected_tools:
        assert (
            expected_tool in tool_names
        ), f"Expected tool '{expected_tool}' not found in {tool_names}"
