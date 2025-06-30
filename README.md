# 🚀 MCP Server Template

A robust, production-ready template for building FastMCP servers with Docker support, automated deployment, and comprehensive tooling.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0+-green.svg)](https://github.com/jlowin/fastmcp)

## 📋 Overview

This template provides a complete foundation for building Model Context Protocol (MCP) servers using FastMCP 2.0. It includes Docker containerization, automated builds, health monitoring, and production-ready configurations.

### ✨ Features

- **🏗️ FastMCP 2.0 Integration** - Latest MCP server framework
- **🐳 Docker Support** - Complete containerization with multi-stage builds
- **🌐 Multiple Transports** - Streamable HTTP, SSE, and STDIO support
- **📊 Health Monitoring** - Built-in health checks and logging
- **🔧 Development Tools** - Testing framework and debugging utilities
- **📚 Comprehensive Documentation** - Detailed guides and examples
- **🚀 Production Ready** - Security, performance, and scalability considerations
- **🔄 CI/CD Ready** - Automated build and deployment scripts

## 🏗️ Architecture

```
MCP-Server-Template/
├── src/
│   ├── server.py                 # Main MCP server implementation
│   ├── tools/                    # MCP tools directory
│   │   ├── __init__.py
│   │   ├── example_tools.py      # Example tool implementations
│   │   └── base.py              # Base tool classes
│   ├── resources/               # MCP resources directory
│   │   ├── __init__.py
│   │   └── example_resources.py # Example resource implementations
│   ├── prompts/                 # MCP prompts directory
│   │   ├── __init__.py
│   │   └── example_prompts.py   # Example prompt implementations
│   └── config/
│       ├── __init__.py
│       └── settings.py          # Configuration management
├── docker/
│   ├── Dockerfile               # Multi-stage production build
│   ├── docker-compose.yml       # Development environment
│   ├── entrypoint.sh           # Container initialization
│   └── .dockerignore           # Docker build optimization
├── scripts/
│   ├── build.sh                # Linux/macOS build script
│   ├── build.cmd               # Windows build script
│   ├── test.py                 # Testing utilities
│   └── deploy.sh              # Deployment automation
├── tests/
│   ├── test_server.py          # Server integration tests
│   ├── test_tools.py           # Tool unit tests
│   └── conftest.py             # pytest configuration
├── docs/
│   ├── quickstart.md           # Quick start guide
│   ├── development.md          # Development guide
│   ├── deployment.md           # Deployment guide
│   ├── api-reference.md        # API documentation
│   └── examples/               # Usage examples
├── pyproject.toml              # Python dependencies
├── uv.lock                     # Dependency lock file
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- UV package manager (recommended)

### 1. Clone and Setup

```bash
# Clone the template
git clone [<your-repo-url> my-mcp-server](https://github.com/sandeep-13-dev/MCP-Server-Template.git)
cd my-mcp-server

# Install dependencies
uv sync
```

### 2. Configure Your Server

Edit `src/config/settings.py`:

```python
SERVER_NAME = "My Awesome MCP Server"
SERVER_VERSION = "1.0.0"
SERVER_DESCRIPTION = "Description of your MCP server"
```

### 3. Add Your Tools

Create tools in `src/tools/`:

```python
from fastmcp import FastMCP
from typing import Dict, Any

mcp = FastMCP("My Server")

@mcp.tool
async def my_custom_tool(param: str) -> Dict[str, Any]:
    """Your custom tool implementation"""
    return {"result": f"Processed: {param}"}
```

### 4. Run Locally

```bash
# Development mode
python src/server.py

# Or with UV
uv run src/server.py
```

### 5. Build and Deploy with Docker

```bash
# Build container
docker-compose build

# Run in production mode
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

## 🛠️ Development

### Project Structure

#### Core Components

- **`src/server.py`** - Main FastMCP server with lifecycle management
- **`src/tools/`** - MCP tool implementations with async support
- **`src/resources/`** - Resource providers and templates
- **`src/prompts/`** - Prompt templates and generators
- **`src/config/`** - Configuration management and environment variables

#### Development Tools

- **`scripts/test.py`** - Comprehensive testing framework
- **`scripts/build.sh/.cmd`** - Cross-platform build automation
- **`docker/`** - Complete containerization setup
- **`tests/`** - Unit and integration test suites

### Adding New Tools

1. Create a new file in `src/tools/`
2. Implement your tool using the `@mcp.tool` decorator
3. Add imports to `src/tools/__init__.py`
4. Write tests in `tests/test_tools.py`

Example tool:

```python
# src/tools/my_tools.py
from fastmcp import FastMCP
from typing import Dict, Any, Optional
import asyncio

mcp = FastMCP.get_instance()  # Get shared instance

@mcp.tool
async def process_data(
    data: str, 
    format_type: str = "json",
    timeout: Optional[int] = 30
) -> Dict[str, Any]:
    """
    Process data with specified format.
    
    Args:
        data: Input data to process
        format_type: Output format (json, xml, csv)
        timeout: Processing timeout in seconds
    
    Returns:
        Dict containing processed result
    """
    try:
        # Your processing logic here
        await asyncio.sleep(0.1)  # Simulate async work
        
        return {
            "success": True,
            "result": f"Processed {len(data)} characters as {format_type}",
            "timestamp": "2024-12-26T10:00:00Z"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### Configuration Management

Environment variables are managed through `src/config/settings.py`:

```python
# src/config/settings.py
import os
from typing import Optional

class Settings:
    # Server Configuration
    SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "MCP Server Template")
    SERVER_VERSION: str = os.getenv("MCP_SERVER_VERSION", "1.0.0")
    SERVER_DESCRIPTION: str = os.getenv("MCP_SERVER_DESCRIPTION", "A template MCP server")
    
    # Network Configuration
    HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("MCP_PORT", "8000"))
    
    # Feature Flags
    ENABLE_HEALTH_CHECK: bool = os.getenv("ENABLE_HEALTH_CHECK", "true").lower() == "true"
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    
    # Security
    API_KEY: Optional[str] = os.getenv("API_KEY")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

settings = Settings()
```

## 🐳 Docker Deployment

### Production Build

The template includes a multi-stage Dockerfile optimized for production:

```dockerfile
# Optimized for size and security
FROM python:3.11-slim as production

# Non-root user for security
RUN useradd --create-home --shell /bin/bash mcp
USER mcp

# Minimal dependencies
COPY --chown=mcp:mcp . /app
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python scripts/healthcheck.py

EXPOSE 8000
CMD ["python", "src/server.py"]
```

### Environment Variables

Configure your deployment with these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_SERVER_NAME` | Server display name | "MCP Server Template" |
| `MCP_HOST` | Bind address | "0.0.0.0" |
| `MCP_PORT` | Server port | "8000" |
| `MCP_TRANSPORT` | Transport type (http/sse/stdio) | "http" |
| `LOG_LEVEL` | Logging level | "INFO" |
| `ENABLE_HEALTH_CHECK` | Enable health endpoint | "true" |
| `API_KEY` | Optional API key for authentication | None |

### Build Scripts

Use the provided build scripts for consistent deployments:

```bash
# Linux/macOS
./scripts/build.sh --production --push --tag v1.0.0

# Windows
./scripts/build.cmd --production --push --tag v1.0.0
```

## 📊 Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_tools.py

# Run integration tests
uv run pytest tests/test_server.py
```

### Test Structure

```python
# tests/test_tools.py
import pytest
from fastmcp import Client
from src.server import create_server

@pytest.fixture
async def mcp_client():
    """Create a test MCP client."""
    server = create_server()
    client = Client(server)
    async with client:
        yield client

async def test_process_data_tool(mcp_client):
    """Test the process_data tool."""
    result = await mcp_client.call_tool("process_data", {
        "data": "test data",
        "format_type": "json"
    })
    
    assert result[0].text is not None
    data = json.loads(result[0].text)
    assert data["success"] is True
    assert "result" in data
```

## 🌐 Client Integration

### Cursor IDE

Add to your Cursor settings:

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

Add to your Claude Desktop configuration:

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

### Custom Python Client

```python
from fastmcp import Client
import asyncio

async def use_mcp_server():
    client = Client("http://localhost:8000/mcp")
    
    async with client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # Use a tool
        result = await client.call_tool("process_data", {
            "data": "Hello, MCP!",
            "format_type": "json"
        })
        print(f"Result: {result[0].text}")

asyncio.run(use_mcp_server())
```

## 🔧 Customization

### Server Lifecycle

The template includes comprehensive lifecycle management:

```python
# src/server.py
from contextlib import asynccontextmanager
from fastmcp import FastMCP

@asynccontextmanager
async def lifespan(app):
    """Manage server lifecycle."""
    print("🚀 Server starting...")
    
    # Startup logic
    await initialize_resources()
    await setup_monitoring()
    
    yield
    
    # Shutdown logic
    await cleanup_resources()
    print("🛑 Server stopped")

def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    mcp = FastMCP(
        name=settings.SERVER_NAME,
        version=settings.SERVER_VERSION,
        description=settings.SERVER_DESCRIPTION
    )
    
    # Import all tools, resources, and prompts
    from src.tools import *
    from src.resources import *
    from src.prompts import *
    
    return mcp
```

### Adding Authentication

```python
# src/config/auth.py
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from src.config.settings import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key if authentication is enabled."""
    if settings.API_KEY and api_key != settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return api_key
```

## 📈 Production Considerations

### Performance

- **Async Design**: All tools use async/await for optimal performance
- **Connection Pooling**: Efficient resource management
- **Memory Management**: Proper cleanup and garbage collection
- **Caching**: Built-in caching strategies for frequently accessed data

### Security

- **Non-root Container**: Docker containers run as non-privileged user
- **API Key Authentication**: Optional API key protection
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Input Validation**: Comprehensive input sanitization

### Monitoring

- **Health Checks**: Built-in health monitoring endpoints
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Metrics Collection**: Optional metrics export
- **Error Tracking**: Comprehensive error handling and reporting

### Scalability

- **Stateless Design**: Horizontal scaling ready
- **Resource Limits**: Configurable memory and CPU limits
- **Load Balancing**: Compatible with standard load balancers
- **Database Integration**: Ready for external data stores

## 📚 Documentation

- **[Quick Start Guide](docs/quickstart.md)** - Get up and running in 5 minutes
- **[Development Guide](docs/development.md)** - Detailed development workflow
- **[Deployment Guide](docs/deployment.md)** - Production deployment strategies
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Examples](docs/examples/)** - Real-world implementation examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) - The excellent MCP framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol specification
- [Docker](https://www.docker.com/) - Containerization platform

---

**Built with ❤️ for the MCP community** 
