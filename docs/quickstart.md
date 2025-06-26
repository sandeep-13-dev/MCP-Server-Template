# 🚀 Quick Start Guide

Get your MCP Server Template up and running in 5 minutes!

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **UV package manager** (recommended) - `pip install uv`
- **Docker & Docker Compose** (optional, for containerized deployment)
- **Git** - For cloning the repository

## 📥 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url> my-mcp-server
cd my-mcp-server
```

### 2. Install Dependencies

Using UV (recommended):
```bash
uv sync
```

Using pip:
```bash
pip install -e .
```

For development with additional tools:
```bash
uv sync --extra dev
# or
pip install -e ".[dev]"
```

## ⚙️ Basic Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# Server Configuration
MCP_SERVER_NAME="My Awesome MCP Server"
MCP_SERVER_VERSION="1.0.0"
MCP_SERVER_DESCRIPTION="My custom MCP server"

# Network Settings
MCP_HOST="0.0.0.0"
MCP_PORT="8000"
MCP_TRANSPORT="http"

# Features
ENABLE_HEALTH_CHECK="true"
ENABLE_METRICS="false"
DEBUG="false"

# Optional: Security
# API_KEY="your-secret-key"
```

### 2. Update Server Settings

Edit `src/config/settings.py` to customize your server:

```python
# Minimal configuration example
SERVER_NAME = "My Awesome MCP Server"
SERVER_DESCRIPTION = "A server that does amazing things"
```

## 🏃‍♂️ Running the Server

### Local Development

```bash
# Using Python directly
python src/server.py

# Using UV
uv run src/server.py

# With environment variables
MCP_PORT=8080 python src/server.py
```

The server will start and display:
```
🌐 Starting My Awesome MCP Server on 0.0.0.0:8000
📡 Transport: http
🔗 Endpoint: http://0.0.0.0:8000/mcp
📋 Description: A robust template for building FastMCP servers
🚀 Initializing My Awesome MCP Server v1.0.0
📊 Loaded 1 tools
📚 Loaded 4 resources
💬 Loaded 5 prompts
📊 Setting up health monitoring...
✅ My Awesome MCP Server initialized successfully
```

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t my-mcp-server .
docker run -p 8000:8000 my-mcp-server
```

## 🧪 Testing Your Server

### 1. Health Check

```bash
# Test the health endpoint
curl http://localhost:8000/mcp

# Using the health check script
python scripts/healthcheck.py
```

### 2. Using MCP Client

Create a test script `test_client.py`:

```python
import asyncio
from fastmcp import Client

async def test_server():
    client = Client("http://localhost:8000/mcp")
    
    async with client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # Test a tool
        result = await client.call_tool("echo", {"message": "Hello, MCP!"})
        print(f"Echo result: {result[0].text}")

# Run the test
asyncio.run(test_server())
```

Run the test:
```bash
python test_client.py
```

## 🛠️ Adding Your First Custom Tool

### 1. Create a New Tool Module

Create `src/tools/my_tools.py`:

```python
from fastmcp import FastMCP
from typing import Dict, Any

# Get the shared MCP instance
mcp = FastMCP("My Awesome MCP Server")

@mcp.tool
async def calculate_sum(a: float, b: float) -> Dict[str, Any]:
    """
    Calculate the sum of two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Dict containing the sum
    """
    result = a + b
    return {
        "success": True,
        "result": result,
        "operation": "addition",
        "inputs": {"a": a, "b": b}
    }

@mcp.tool
async def greet_user(name: str, language: str = "en") -> Dict[str, Any]:
    """
    Greet a user in different languages.
    
    Args:
        name: User's name
        language: Language code (en, es, fr, de)
        
    Returns:
        Dict containing the greeting
    """
    greetings = {
        "en": f"Hello, {name}!",
        "es": f"¡Hola, {name}!",
        "fr": f"Bonjour, {name}!",
        "de": f"Hallo, {name}!"
    }
    
    greeting = greetings.get(language, greetings["en"])
    
    return {
        "success": True,
        "greeting": greeting,
        "language": language,
        "name": name
    }
```

### 2. Register Your Tool Module

Edit `src/tools/__init__.py` and add your module to the TOOL_MODULES list:

```python
TOOL_MODULES = [
    "tools.example_tools",
    "tools.my_tools",  # Add this line
]
```

### 3. Test Your New Tools

Restart your server and test:

```python
import asyncio
from fastmcp import Client

async def test_new_tools():
    client = Client("http://localhost:8000/mcp")
    
    async with client:
        # Test the sum tool
        result = await client.call_tool("calculate_sum", {"a": 5, "b": 3})
        print(f"Sum result: {result[0].text}")
        
        # Test the greeting tool
        result = await client.call_tool("greet_user", {
            "name": "Alice", 
            "language": "es"
        })
        print(f"Greeting result: {result[0].text}")

asyncio.run(test_new_tools())
```

## 🌐 Client Integration

### Cursor IDE

Add this to your Cursor settings (`.cursor/settings.json`):

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "transport": "http",
      "url": "http://localhost:8000/mcp",
      "description": "My custom MCP server"
    }
  }
}
```

### Claude Desktop

Add this to your Claude Desktop config:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8000/mcp"]
    }
  }
}
```

## 🚀 Next Steps

Now that you have a working MCP server, here's what to do next:

1. **📖 Read the [Development Guide](development.md)** - Learn about advanced development patterns
2. **🔧 Explore the [API Reference](api-reference.md)** - Understand all available features
3. **🚀 Check out [Deployment Guide](deployment.md)** - Deploy to production
4. **💡 Browse [Examples](examples/)** - See real-world implementations

## 🆘 Troubleshooting

### Server Won't Start

1. **Check Python version**: `python --version` (must be 3.11+)
2. **Verify dependencies**: `uv sync` or `pip install -e .`
3. **Check port availability**: `lsof -i :8000` (macOS/Linux) or `netstat -an | findstr :8000` (Windows)
4. **Review logs**: Look for error messages in the console output

### Connection Issues

1. **Firewall**: Ensure port 8000 is open
2. **Host binding**: Try changing `MCP_HOST` to `127.0.0.1` for local-only access
3. **Health check**: Run `python scripts/healthcheck.py`

### Tool Registration Issues

1. **Import errors**: Check that your tool modules are importable
2. **Syntax errors**: Verify your tool functions are properly decorated
3. **Module loading**: Ensure your module is listed in `TOOL_MODULES`

### Getting Help

- **📚 Documentation**: Check other docs in the `docs/` folder
- **🐛 Issues**: Create an issue on GitHub
- **💬 Community**: Join our discussion forums

## 📊 Monitoring

Your server includes built-in monitoring capabilities:

### Health Endpoint
```bash
curl http://localhost:8000/mcp
```

### Health Check Tool
```bash
python scripts/healthcheck.py
```

### Log Monitoring
Check your logs for errors and performance information. In development mode, logs appear in the console.

---

**🎉 Congratulations!** You now have a working MCP server. The server is designed to be production-ready and scalable. Explore the other documentation to learn about advanced features and deployment options. 