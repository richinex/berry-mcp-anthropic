"""
Tests for CLI functionality using FastMCP
"""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_run_stdio_server():
    """Test stdio server run function"""
    from berry_mcp.server import run_stdio_server

    # Mock FastMCP and dependencies
    with patch("berry_mcp.server.create_server") as mock_create_server:
        mock_server = MagicMock()
        mock_server.run = MagicMock()
        mock_create_server.return_value = mock_server

        run_stdio_server()

        # Verify server was created and run
        mock_create_server.assert_called_once_with(None, None, "INFO")
        mock_server.run.assert_called_once_with(transport="stdio")


def test_run_stdio_server_with_tool_modules():
    """Test stdio server with custom tool modules"""
    from berry_mcp.server import run_stdio_server

    # Mock tool modules
    mock_module1 = MagicMock()
    mock_module2 = MagicMock()
    tool_modules = [mock_module1, mock_module2]

    with patch("berry_mcp.server.create_server") as mock_create_server:
        mock_server = MagicMock()
        mock_server.run = MagicMock()
        mock_create_server.return_value = mock_server

        run_stdio_server(tool_modules=tool_modules, server_name="custom-server")

        # Verify server was created with tool modules
        mock_create_server.assert_called_once_with(
            tool_modules, "custom-server", "INFO"
        )
        mock_server.run.assert_called_once_with(transport="stdio")


@pytest.mark.asyncio
async def test_run_http_server():
    """Test HTTP server run function"""
    # Skip this test - FastMCP doesn't have separate HTTP server function in our implementation
    pytest.skip("HTTP server testing requires complex import mocking")


@pytest.mark.asyncio
async def test_run_http_server_missing_fastapi():
    """Test HTTP server gracefully handles missing FastAPI"""
    # Skip this test - FastMCP doesn't have separate HTTP server function in our implementation
    pytest.skip("HTTP server testing requires complex import mocking")


def test_cli_main_stdio():
    """Test CLI main function (stdio is the only transport in FastMCP)"""
    from berry_mcp.server import cli_main

    test_args = ["berry-mcp"]

    with (
        patch("sys.argv", test_args),
        patch("berry_mcp.server.run_stdio_server") as mock_run_stdio,
    ):

        cli_main()

        # Should have called run_stdio_server directly (no asyncio.run needed)
        mock_run_stdio.assert_called_once()


def test_cli_main_http():
    """Test CLI main function - no HTTP transport in FastMCP version"""
    # Skip this test - FastMCP only supports stdio transport in our implementation
    pytest.skip("HTTP transport not implemented in FastMCP version")


def test_cli_main_help():
    """Test CLI help message"""
    from berry_mcp.server import cli_main

    test_args = ["berry-mcp", "--help"]

    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit) as exc_info:
            cli_main()
        # Help should exit with status 0
        assert exc_info.value.code == 0


def test_cli_main_invalid_transport():
    """Test CLI with invalid transport (should not exist in FastMCP)"""
    # FastMCP only supports stdio, so this test doesn't apply
    pytest.skip("FastMCP only supports stdio transport")


def test_main_backwards_compatibility():
    """Test the main() function for backwards compatibility"""
    from berry_mcp.server import main

    with patch("berry_mcp.server.run_stdio_server") as mock_run_stdio:
        # Call the backwards compatibility main function (now synchronous)
        main()

        # Should have called run_stdio_server
        mock_run_stdio.assert_called_once()


def test_server_name_from_env():
    """Test server name can be set from environment variable"""
    from berry_mcp.server import cli_main

    test_args = ["berry-mcp"]
    old_name = os.environ.get("BERRY_MCP_SERVER_NAME")

    try:
        os.environ["BERRY_MCP_SERVER_NAME"] = "env-test-server"

        with (
            patch("sys.argv", test_args),
            patch("berry_mcp.server.run_stdio_server") as mock_run_stdio,
        ):

            cli_main()

            # Check that run_stdio_server was called with env server name
            mock_run_stdio.assert_called_once()
            args, kwargs = mock_run_stdio.call_args
            assert kwargs.get("server_name") == "env-test-server"

    finally:
        if old_name is not None:
            os.environ["BERRY_MCP_SERVER_NAME"] = old_name
        elif "BERRY_MCP_SERVER_NAME" in os.environ:
            del os.environ["BERRY_MCP_SERVER_NAME"]


def test_load_tools_from_path():
    """Test loading tools from custom path"""
    from berry_mcp.server import cli_main

    test_args = ["berry-mcp", "--tools-path", "custom.tools,other.tools"]

    with (
        patch("sys.argv", test_args),
        patch("berry_mcp.server.run_stdio_server") as mock_run_stdio,
        patch("importlib.import_module") as mock_import,
    ):

        mock_module1 = MagicMock()
        mock_module2 = MagicMock()
        mock_import.side_effect = [mock_module1, mock_module2]

        cli_main()

        # Should have attempted to import both modules
        assert mock_import.call_count == 2
        mock_import.assert_any_call("custom.tools")
        mock_import.assert_any_call("other.tools")

        # Should have called run_stdio_server with tool modules
        mock_run_stdio.assert_called_once()
        args, kwargs = mock_run_stdio.call_args
        assert kwargs.get("tool_modules") == [mock_module1, mock_module2]


def test_cli_example_usage():
    """Test that CLI can be imported and called without errors"""
    from berry_mcp.server import cli_main

    # This just tests that the function exists and can be called
    # (actual functionality is tested in other tests with mocking)
    assert callable(cli_main)


def test_server_error_handling():
    """Test that server errors are handled gracefully"""
    from berry_mcp.server import cli_main

    test_args = ["berry-mcp"]

    with (
        patch("sys.argv", test_args),
        patch("asyncio.run") as mock_asyncio_run,
        patch("sys.exit") as mock_exit,
    ):

        # Simulate a server error
        mock_asyncio_run.side_effect = RuntimeError("Test error")

        cli_main()

        # Should exit with error code
        mock_exit.assert_called_once_with(1)
