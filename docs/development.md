# 🛠️ Development Guide

Comprehensive guide for developing with the MCP Server Template, covering advanced patterns, testing, debugging, and best practices.

## 📁 Project Structure Deep Dive

```
MCP-Server-Template/
├── src/                          # Source code
│   ├── server.py                 # Main server implementation with lifecycle management
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py           # Environment variables and validation
│   ├── tools/                    # MCP tools (your main business logic)
│   │   ├── __init__.py           # Tool loading and registration
│   │   ├── base.py              # Base classes and utilities
│   │   └── example_tools.py     # Example tool implementations
│   ├── resources/               # MCP resources (templates, documents)
│   │   ├── __init__.py          # Resource loading
│   │   └── example_resources.py # Example resource implementations
│   ├── prompts/                 # MCP prompts (LLM interaction templates)
│   │   ├── __init__.py          # Prompt loading
│   │   └── example_prompts.py   # Example prompt implementations
├── tests/                       # Test suite
│   ├── conftest.py             # pytest configuration and fixtures
│   ├── test_server.py          # Server integration tests
│   └── test_tools.py           # Tool unit tests
├── docker/                      # Containerization
│   ├── Dockerfile              # Multi-stage production build
│   ├── docker-compose.yml      # Development environment
│   └── .dockerignore           # Docker build optimization
├── scripts/                     # Utility scripts
│   ├── build.sh               # Build automation (Linux/macOS)
│   ├── build.cmd              # Build automation (Windows)
│   └── healthcheck.py         # Health monitoring
└── docs/                        # Documentation
    ├── quickstart.md
    ├── development.md          # This file
    ├── deployment.md
    ├── api-reference.md
    └── examples/
```

## 🏗️ Architecture Overview

### Server Lifecycle

The MCP server follows a structured lifecycle with proper resource management:

```python
# src/server.py
class MCPServerTemplate:
    async def initialize(self):
        """Startup sequence"""
        # 1. Create FastMCP instance
        # 2. Load tools, resources, prompts
        # 3. Setup health monitoring
        # 4. Initialize metrics
        
    async def cleanup(self):
        """Shutdown sequence"""
        # 1. Stop background tasks
        # 2. Close connections
        # 3. Save state
        # 4. Cleanup resources
```

### Component Loading

Components are loaded dynamically for flexibility:

```python
# src/tools/__init__.py
TOOL_MODULES = [
    "tools.example_tools",
    "tools.data_processing",     # Your custom modules
    "tools.api_integrations",
]

async def load_tools(mcp: FastMCP) -> int:
    """Dynamic tool loading with error handling"""
    for module_name in TOOL_MODULES:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            logger.warning(f"Failed to import {module_name}: {e}")
```

## 🔧 Tool Development Patterns

### Basic Tool Structure

```python
from fastmcp import FastMCP
from typing import Dict, Any, Optional
import asyncio

mcp = FastMCP("My Server")

@mcp.tool
async def my_tool(
    required_param: str,
    optional_param: Optional[int] = None
) -> Dict[str, Any]:
    """
    Tool description for MCP client.
    
    Args:
        required_param: Description of required parameter
        optional_param: Description of optional parameter
        
    Returns:
        Dict containing the result
    """
    # Your implementation here
    return {"result": "success"}
```

### Advanced Tool Patterns

#### 1. Tools with Input Validation

```python
from .base import validate_required_params, ToolError

@mcp.tool
@validate_required_params("data", "format")
async def process_data(
    data: str,
    format: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process data with validation."""
    
    # Validate format
    valid_formats = ["json", "xml", "csv"]
    if format not in valid_formats:
        raise ToolError(
            f"Invalid format: {format}. Must be one of {valid_formats}",
            "INVALID_FORMAT"
        )
    
    # Validate data length
    if len(data) > 1000000:  # 1MB limit
        raise ToolError("Data too large", "DATA_TOO_LARGE")
    
    # Process the data
    result = await process_data_async(data, format, options or {})
    
    return {
        "success": True,
        "result": result,
        "format": format,
        "processed_at": datetime.now().isoformat()
    }
```

#### 2. Tools with Retry Logic

```python
from .base import tool_retry, tool_timeout

@mcp.tool
@tool_retry(max_attempts=3, delay=1.0, backoff=2.0)
@tool_timeout(30)
async def external_api_call(
    endpoint: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Call external API with retry logic."""
    
    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, params=params)
        
        if response.status_code == 429:  # Rate limited
            raise ToolError("Rate limited", "RATE_LIMITED", retry=True)
        
        if response.status_code >= 500:  # Server error
            raise ToolError("Server error", "SERVER_ERROR", retry=True)
        
        response.raise_for_status()
        return response.json()
```

#### 3. Tools with Background Tasks

```python
import asyncio
from typing import Dict, Any

@mcp.tool
async def start_background_job(
    job_type: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Start a background job and return job ID."""
    
    job_id = f"job_{int(time.time())}"
    
    # Start background task
    task = asyncio.create_task(
        run_background_job(job_id, job_type, parameters)
    )
    
    # Store task reference (in production, use a proper job queue)
    background_tasks[job_id] = task
    
    return {
        "job_id": job_id,
        "status": "started",
        "job_type": job_type
    }

@mcp.tool
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """Get status of a background job."""
    
    if job_id not in background_tasks:
        raise ToolError("Job not found", "JOB_NOT_FOUND")
    
    task = background_tasks[job_id]
    
    if task.done():
        try:
            result = task.result()
            return {"job_id": job_id, "status": "completed", "result": result}
        except Exception as e:
            return {"job_id": job_id, "status": "failed", "error": str(e)}
    else:
        return {"job_id": job_id, "status": "running"}
```

### Tool Base Classes

Use the base classes for consistent behavior:

```python
# src/tools/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseTool(ABC):
    """Base class for MCP tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool."""
        pass
    
    async def validate_inputs(self, **kwargs) -> None:
        """Validate tool inputs."""
        pass

class DataProcessingTool(BaseTool):
    """Base class for data processing tools."""
    
    async def validate_inputs(self, **kwargs) -> None:
        if "data" not in kwargs:
            raise ToolError("Data parameter required", "MISSING_DATA")
```

## 📚 Resource Development

Resources provide templates and documents to MCP clients:

```python
# src/resources/my_resources.py
from fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.resource("template://python-class")
async def python_class_template(
    class_name: str,
    methods: List[str] = None
) -> str:
    """Generate a Python class template."""
    
    methods = methods or ["__init__"]
    
    template = f"""class {class_name}:
    \"\"\"Class description.\"\"\"
    
    def __init__(self):
        \"\"\"Initialize {class_name}.\"\"\"
        pass
"""
    
    for method in methods:
        if method != "__init__":
            template += f"""
    def {method}(self):
        \"\"\"Method description.\"\"\"
        pass
"""
    
    return template

@mcp.resource("docs://api-spec")
async def api_specification() -> str:
    """Provide API specification."""
    return """
    # API Specification
    
    ## Endpoints
    
    ### GET /api/v1/data
    Returns data in JSON format.
    
    ### POST /api/v1/process
    Processes submitted data.
    """
```

## 💬 Prompt Development

Prompts help structure LLM interactions:

```python
# src/prompts/my_prompts.py
from fastmcp import FastMCP
from typing import List, Optional

mcp = FastMCP("My Server")

@mcp.prompt("system-analysis")
async def system_analysis_prompt(
    system_type: str,
    requirements: List[str],
    constraints: Optional[List[str]] = None
) -> str:
    """Generate system analysis prompt."""
    
    requirements_text = "\n".join([f"- {req}" for req in requirements])
    constraints_text = ""
    
    if constraints:
        constraints_text = f"""
Constraints:
{chr(10).join([f"- {constraint}" for constraint in constraints])}
"""
    
    return f"""Analyze the following {system_type} system:

Requirements:
{requirements_text}
{constraints_text}

Please provide:
1. System architecture overview
2. Component breakdown
3. Technology recommendations
4. Implementation timeline
5. Risk assessment
6. Testing strategy

Format your response with clear sections and actionable recommendations.
"""
```

## 🧪 Testing

### Test Structure

```python
# tests/conftest.py
import pytest
import asyncio
from fastmcp import Client
from src.server import create_server

@pytest.fixture
async def mcp_client():
    """Create a test MCP client."""
    server = create_server()
    client = Client(server)
    async with client:
        yield client

@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
```

### Unit Tests

```python
# tests/test_tools.py
import pytest
import json
from fastmcp import Client

class TestTools:
    """Test suite for MCP tools."""
    
    async def test_echo_tool(self, mcp_client):
        """Test the echo tool."""
        result = await mcp_client.call_tool("echo", {
            "message": "test message"
        })
        
        assert result[0].text is not None
        data = json.loads(result[0].text)
        assert data["success"] is True
        assert data["data"]["echoed_message"] == "test message"
    
    async def test_calculate_statistics(self, mcp_client):
        """Test statistics calculation."""
        result = await mcp_client.call_tool("calculate_statistics", {
            "numbers": [1, 2, 3, 4, 5],
            "precision": 2
        })
        
        data = json.loads(result[0].text)
        assert data["success"] is True
        assert data["data"]["mean"] == 3.0
        assert data["data"]["count"] == 5
    
    async def test_tool_error_handling(self, mcp_client):
        """Test tool error handling."""
        with pytest.raises(Exception):
            await mcp_client.call_tool("calculate_statistics", {
                "numbers": [],  # Empty list should cause error
                "precision": 2
            })
    
    @pytest.mark.slow
    async def test_async_tool_timeout(self, mcp_client):
        """Test async tool with timeout."""
        result = await mcp_client.call_tool("simulate_async_work", {
            "duration": 0.1,
            "should_fail": False
        })
        
        data = json.loads(result[0].text)
        assert data["success"] is True
```

### Integration Tests

```python
# tests/test_server.py
import pytest
import httpx
from src.server import MCPServerTemplate

class TestServer:
    """Integration tests for the MCP server."""
    
    @pytest.fixture
    async def server(self):
        """Create and initialize server."""
        server = MCPServerTemplate()
        await server.initialize()
        yield server
        await server.cleanup()
    
    async def test_server_initialization(self, server):
        """Test server initializes correctly."""
        assert server.is_initialized is True
        assert server.mcp is not None
    
    async def test_health_check_tool(self, mcp_client):
        """Test health check functionality."""
        result = await mcp_client.call_tool("health_check", {})
        
        data = json.loads(result[0].text)
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    async def test_server_lifecycle(self):
        """Test complete server lifecycle."""
        server = MCPServerTemplate()
        
        # Test initialization
        await server.initialize()
        assert server.is_initialized is True
        
        # Test cleanup
        await server.cleanup()
        assert server.is_initialized is False
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_tools.py

# Run with markers
pytest -m "not slow"  # Skip slow tests
pytest -m "integration"  # Only integration tests

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

## 🐛 Debugging

### Development Mode

Enable debug mode for detailed logging:

```bash
# Environment variable
DEBUG=true python src/server.py

# Or in settings.py
DEBUG = True
LOG_LEVEL = "DEBUG"
```

### Logging Configuration

```python
# src/config/settings.py
import logging

def configure_debug_logging():
    """Configure detailed debug logging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('debug.log')
        ]
    )
    
    # Set specific loggers
    logging.getLogger('fastmcp').setLevel(logging.DEBUG)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
```

### Debugging Tools

#### 1. Interactive Debugging

```python
# Add breakpoints in your tools
@mcp.tool
async def debug_tool(data: str) -> Dict[str, Any]:
    import pdb; pdb.set_trace()  # Breakpoint
    
    # Process data
    result = process_data(data)
    return {"result": result}
```

#### 2. Debug Tool for Development

```python
@mcp.tool
async def debug_server_state() -> Dict[str, Any]:
    """Debug tool to inspect server state."""
    return {
        "server_name": settings.SERVER_NAME,
        "is_initialized": server_instance.is_initialized,
        "tools_count": len(mcp._tools),
        "resources_count": len(mcp._resources),
        "prompts_count": len(mcp._prompts),
        "settings": settings.to_dict()
    }
```

#### 3. Request/Response Logging

```python
# Add middleware for request logging
@mcp.middleware
async def log_requests(request, call_next):
    start_time = time.time()
    
    logger.debug(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.debug(f"Response: {response.status_code} in {process_time:.3f}s")
    
    return response
```

## 🔄 Configuration Management

### Environment-Specific Configurations

```python
# src/config/settings.py
class DevelopmentSettings(Settings):
    """Development-specific settings."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    RELOAD = True
    ENABLE_METRICS = True

class ProductionSettings(Settings):
    """Production-specific settings."""
    DEBUG = False
    LOG_LEVEL = "INFO"
    RELOAD = False
    REQUIRE_AUTH = True

# Select configuration based on environment
def get_settings():
    env = os.getenv("ENVIRONMENT", "production").lower()
    
    if env == "development":
        return DevelopmentSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return ProductionSettings()

settings = get_settings()
```

### Configuration Validation

```python
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Settings with Pydantic validation."""
    
    SERVER_NAME: str = "MCP Server"
    PORT: int = 8000
    API_KEY: Optional[str] = None
    
    @validator('PORT')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @validator('SERVER_NAME')
    def validate_server_name(cls, v):
        if len(v) < 3:
            raise ValueError('Server name must be at least 3 characters')
        return v
    
    class Config:
        env_file = ".env"
        env_prefix = "MCP_"
```

## 🚀 Performance Optimization

### Async Best Practices

```python
# Good: Concurrent operations
async def process_multiple_items(items: List[str]) -> List[Dict[str, Any]]:
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]

# Good: Connection pooling
async def make_api_calls(endpoints: List[str]) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        tasks = [client.get(endpoint) for endpoint in endpoints]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
```

### Caching Strategies

```python
from functools import lru_cache
import asyncio

# Simple in-memory cache
cache = {}

async def cached_operation(key: str) -> Any:
    if key in cache:
        return cache[key]
    
    result = await expensive_operation(key)
    cache[key] = result
    return result

# TTL cache with asyncio
import time

class TTLCache:
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    
    async def get(self, key: str, factory_func):
        now = time.time()
        
        if key in self.cache:
            value, timestamp = self.cache[key]
            if now - timestamp < self.ttl:
                return value
        
        value = await factory_func()
        self.cache[key] = (value, now)
        return value
```

### Memory Management

```python
import gc
import psutil

@mcp.tool
async def memory_usage() -> Dict[str, Any]:
    """Monitor memory usage."""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        "rss": memory_info.rss,
        "vms": memory_info.vms,
        "percent": process.memory_percent(),
        "gc_counts": gc.get_count()
    }

# Force garbage collection for long-running operations
async def cleanup_after_operation():
    gc.collect()
```

## 📦 Packaging and Distribution

### Building Packages

```bash
# Build wheel
python -m build

# Build with UV
uv build

# Install locally
pip install -e .
```

### Docker Optimization

```dockerfile
# Multi-stage build for smaller images
FROM python:3.11-slim as builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . .
```

## 🔐 Security Considerations

### Input Validation

```python
import re
from typing import Any

def sanitize_input(value: Any) -> str:
    """Sanitize user input."""
    if not isinstance(value, str):
        value = str(value)
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', value)
    return sanitized[:1000]  # Limit length

@mcp.tool
async def secure_tool(user_input: str) -> Dict[str, Any]:
    """Tool with input sanitization."""
    sanitized_input = sanitize_input(user_input)
    # Process sanitized input
    return {"result": f"Processed: {sanitized_input}"}
```

### API Key Authentication

```python
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if settings.API_KEY and api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key
```

## 📊 Monitoring and Observability

### Metrics Collection

```python
import time
from collections import defaultdict

# Simple metrics collector
class Metrics:
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
    
    def increment(self, name: str):
        self.counters[name] += 1
    
    def time_operation(self, name: str):
        return TimerContext(self, name)

class TimerContext:
    def __init__(self, metrics: Metrics, name: str):
        self.metrics = metrics
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        duration = time.time() - self.start_time
        self.metrics.timers[self.name].append(duration)

# Usage in tools
metrics = Metrics()

@mcp.tool
async def monitored_tool(data: str) -> Dict[str, Any]:
    metrics.increment("tool_calls")
    
    with metrics.time_operation("tool_execution"):
        result = await process_data(data)
    
    return {"result": result}
```

### Health Monitoring

```python
@mcp.tool
async def detailed_health_check() -> Dict[str, Any]:
    """Comprehensive health check."""
    import psutil
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Application metrics
    tool_count = len(mcp._tools)
    
    return {
        "status": "healthy",
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent
        },
        "application": {
            "tools_count": tool_count,
            "uptime": time.time() - start_time
        }
    }
```

---

This development guide provides the foundation for building robust, scalable MCP servers. Continue to the [Deployment Guide](deployment.md) for production deployment strategies. 