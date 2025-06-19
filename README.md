# Berry MCP Anthropic

[![CI](https://github.com/richinex/berry-mcp-anthropic/actions/workflows/ci.yml/badge.svg)](https://github.com/richinex/berry-mcp-anthropic/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/richinex/berry-mcp-anthropic/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/badge/package%20manager-uv-blue)](https://github.com/astral-sh/uv)

A universal Model Context Protocol (MCP) server framework built on **Anthropic's official MCP SDK** with FastMCP. Makes it easy to create and deploy custom tool servers for AI assistants like Claude.

## ✨ Features

- **🏢 Official MCP SDK**: Built on Anthropic's official MCP SDK with FastMCP
- **🔧 Universal Framework**: Create MCP servers for any type of tools
- **🎯 Simple Tool Creation**: Decorator-based tool registration with automatic JSON schema generation
- **🔌 Plugin Architecture**: Load tools from any Python module or package
- **🚀 Multiple Transports**: Support for stdio transport (FastMCP managed)
- **⚙️ Flexible Configuration**: Environment variables and command-line options
- **📝 Auto-Documentation**: Automatic tool discovery and schema generation
- **🔒 Type Safety**: Full type annotation support with validation
- **📄 PDF Processing**: Built-in PDF text extraction tools with PyMuPDF and PyPDF2

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (when published)
uv add berry-mcp-anthropic

# Or install from source
git clone https://github.com/richinex/berry-mcp-anthropic.git
cd berry-mcp-anthropic
uv pip install -e .
```

### Create Your First Tool

```python
# my_tools.py
from berry_mcp.tools.decorators import tool

@tool(description="Add two numbers together")
def add_numbers(a: float, b: float) -> float:
    """Add two numbers and return the result"""
    return a + b

@tool(description="Generate a greeting message")  
def greet(name: str, title: str = "friend") -> str:
    """Generate a personalized greeting"""
    return f"Hello {title} {name}!"

@tool(description="Extract text from PDF files")
async def process_pdf(file_path: str) -> str:
    """Process PDF and extract text content"""
    # Built-in PDF tools are available automatically
    from berry_mcp.tools.pdf_tools import read_pdf_text
    return await read_pdf_text(file_path)
```

### Run Your Server

```bash
# Load your custom tools
BERRY_MCP_TOOLS_PATH=my_tools uv run python -m berry_mcp

# Or run with built-in tools (includes PDF processing)
uv run python -m berry_mcp

# Test the server is working
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | uv run python -m berry_mcp
```

### VS Code Integration

Add to your `.vscode/mcp.json`:

```json
{
  "inputs": [],
  "servers": {
    "my-custom-tools": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "-m", "berry_mcp"],
      "env": {
        "BERRY_MCP_TOOLS_PATH": "my_tools"
      }
    }
  }
}
```

## 📖 Documentation

- **[VS Code Configuration Guide](docs/VSCODE_CONFIGURATION.md)** - Complete setup instructions
- **[Tool Development Guide](docs/TOOL_DEVELOPMENT.md)** - Create custom tools
- **[API Documentation](docs/API.md)** - Technical reference

## 🛠️ Built-in Tools

Berry MCP Anthropic comes with comprehensive tools to get you started:

- **PDF Processing**: `read_pdf_text`, `read_pdf_text_pypdf2` - Extract text from PDF files
- **Math Operations**: `add_numbers`, `generate_random`
- **Text Processing**: `format_text`, `find_replace_text`, `encode_decode_text`
- **System Info**: `get_system_info`, `generate_uuid`
- **Data Tools**: `validate_json`, `generate_report`
- **Async Examples**: `async_process_text`

All tools are automatically discovered and registered with the FastMCP framework.

## 🔧 Advanced Usage

### Multiple Tool Sources
```bash
BERRY_MCP_TOOLS_PATH="my_tools,web_tools,data_processors" uv run python -m berry_mcp
```

### Custom Server Configuration
```bash
# Custom server name and logging
BERRY_MCP_SERVER_NAME="my-pdf-server" BERRY_MCP_LOG_LEVEL="DEBUG" uv run python -m berry_mcp
```

### Environment Configuration
```bash
export BERRY_MCP_SERVER_NAME="my-custom-server"
export BERRY_MCP_LOG_LEVEL="DEBUG"
export BERRY_MCP_TOOLS_PATH="my_tools,another_module.tools"
uv run python -m berry_mcp
```

## 🏗️ Architecture

Berry MCP Anthropic follows SOLID principles with a clean, extensible architecture built on FastMCP:

- **FastMCP Integration**: Built on Anthropic's official MCP SDK
- **Tool Registry**: Global tool registration with FastMCP integration
- **Auto-Discovery**: Automatic tool loading from modules
- **Decorator Framework**: Simple `@tool` decorator for registration
- **Transport Layer**: FastMCP-managed stdio communication
- **Type Safety**: Full mypy support with proper type annotations

## 📋 Requirements

- Python 3.10+
- Anthropic's MCP SDK (FastMCP)
- Type annotations for automatic schema generation
- Optional: PyMuPDF and PyPDF2 for PDF processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the existing patterns
4. Add tests for new functionality
5. Run the test suite: `uv run pytest tests/`
6. Check code quality: `uv run ruff check src/ && uv run mypy src/`
7. Submit a pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on the [Model Context Protocol](https://modelcontextprotocol.io/)
- Inspired by the need for easy MCP server creation
- Following clean code principles and design patterns

---

**🚀 Start building your custom MCP tools today with Berry MCP Server!**