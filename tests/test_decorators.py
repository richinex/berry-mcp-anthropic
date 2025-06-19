"""
Tests for tool decorators using Anthropic SDK
"""

from berry_mcp.tools.decorators import tool


def test_basic_tool_decorator():
    """Test basic tool decorator functionality with Anthropic SDK"""

    @tool(description="Test tool")
    def test_func(x: int, y: str = "default") -> str:
        """Test function"""
        return f"{x}: {y}"

    # Check that Berry MCP metadata was added for compatibility
    assert hasattr(test_func, "_berry_mcp_metadata")

    berry_metadata = test_func._berry_mcp_metadata
    assert berry_metadata["custom_name"] == "test_func"
    assert berry_metadata["custom_description"] == "Test tool"
    assert berry_metadata["original_name"] == "test_func"


def test_tool_decorator_with_custom_name():
    """Test tool decorator with custom name"""

    @tool(name="custom_name", description="Custom tool")
    def original_name(value: str) -> str:
        return value.upper()

    berry_metadata = original_name._berry_mcp_metadata
    assert berry_metadata["custom_name"] == "custom_name"
    assert berry_metadata["custom_description"] == "Custom tool"
    assert berry_metadata["original_name"] == "original_name"


def test_tool_decorator_uses_docstring():
    """Test that decorator uses function docstring if no description provided"""

    @tool()
    def documented_func() -> str:
        """This is from the docstring"""
        return "test"

    berry_metadata = documented_func._berry_mcp_metadata
    assert berry_metadata["custom_description"] == "This is from the docstring"


def test_tool_decorator_with_examples():
    """Test tool decorator with examples"""

    examples = [{"input": {"x": 1, "y": "test"}, "output": "1: test"}]

    @tool(examples=examples)
    def example_func(x: int, y: str) -> str:
        return f"{x}: {y}"

    berry_metadata = example_func._berry_mcp_metadata
    assert berry_metadata["examples"] == examples


def test_tool_function_still_callable():
    """Test that decorated function is still callable"""

    @tool()
    def callable_test(x: int, y: int = 5) -> int:
        return x + y

    # Function should still work normally
    result = callable_test(10, 15)
    assert result == 25

    # With default parameter
    result = callable_test(10)
    assert result == 15


def test_tool_decorator_preserves_async():
    """Test that async functions work with decorator"""
    import asyncio

    @tool()
    async def async_func(value: str) -> str:
        await asyncio.sleep(0.001)  # Minimal delay
        return value.upper()

    # Function should still be async
    import inspect

    assert inspect.iscoroutinefunction(async_func)

    # Should be callable
    result = asyncio.run(async_func("test"))
    assert result == "TEST"
