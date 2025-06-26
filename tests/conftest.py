"""
Test configuration and fixtures for MCP Server Template.

This module provides common fixtures and configuration for the test suite.
"""

import asyncio
import pytest
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from fastmcp import FastMCP, Client
from src.server import MCPServerTemplate


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def server_instance() -> AsyncGenerator[MCPServerTemplate, None]:
    """
    Create a test MCP server instance.
    
    Yields:
        Initialized MCP server instance
    """
    # Create server instance
    server = MCPServerTemplate()
    
    # Initialize without starting the actual server
    await server.initialize()
    
    yield server
    
    # Cleanup
    await server.cleanup()


@pytest.fixture
async def mcp_client(server_instance: MCPServerTemplate) -> AsyncGenerator[Client, None]:
    """
    Create a test MCP client connected to the test server.
    
    Args:
        server_instance: Test server instance
        
    Yields:
        MCP client connected to test server
    """
    # Create client with the server's MCP instance
    client = Client(server_instance.mcp)
    
    async with client:
        yield client


@pytest.fixture
def mock_settings():
    """
    Mock settings for testing.
    
    Returns:
        Mock settings object
    """
    mock = MagicMock()
    mock.SERVER_NAME = "Test MCP Server"
    mock.SERVER_VERSION = "1.0.0-test"
    mock.SERVER_DESCRIPTION = "Test server"
    mock.HOST = "localhost"
    mock.PORT = 8000
    mock.TRANSPORT = "http"
    mock.ENABLE_HEALTH_CHECK = True
    mock.ENABLE_METRICS = False
    mock.LOG_LEVEL = "DEBUG"
    mock.DEBUG = True
    mock.ENVIRONMENT = "testing"
    mock.is_development = True
    mock.is_production = False
    return mock


@pytest.fixture
def mock_httpx_client():
    """
    Mock httpx client for testing HTTP requests.
    
    Returns:
        Mock httpx client
    """
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "healthy"}
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    return mock_client


@pytest.fixture
def sample_test_data():
    """
    Sample test data for various test scenarios.
    
    Returns:
        Dictionary containing test data
    """
    return {
        "numbers": [1, 2, 3, 4, 5],
        "json_string": '{"name": "test", "value": 42}',
        "text_data": "Hello, World!",
        "config_data": {
            "setting1": "value1",
            "setting2": 123,
            "setting3": True
        }
    }


@pytest.fixture
async def health_checker():
    """
    Create a health checker instance for testing.
    
    Returns:
        Health checker instance
    """
    from scripts.healthcheck import HealthChecker
    return HealthChecker("localhost", 8000)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests that take more than a few seconds"
    )
    config.addinivalue_line(
        "markers", "network: Tests that require network access"
    )


# Test utilities
class MockMCPClient:
    """Mock MCP client for testing."""
    
    def __init__(self):
        """Initialize mock client."""
        self.connected = False
        self.tools = []
        self.resources = []
        self.prompts = []
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.connected = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.connected = False
    
    async def ping(self):
        """Mock ping method."""
        if not self.connected:
            raise ConnectionError("Client not connected")
        return {"status": "pong"}
    
    async def list_tools(self):
        """Mock list tools method."""
        if not self.connected:
            raise ConnectionError("Client not connected")
        return self.tools
    
    async def list_resources(self):
        """Mock list resources method."""
        if not self.connected:
            raise ConnectionError("Client not connected")
        return self.resources
    
    async def list_prompts(self):
        """Mock list prompts method."""
        if not self.connected:
            raise ConnectionError("Client not connected")
        return self.prompts
    
    async def call_tool(self, name: str, parameters: dict = None):
        """Mock call tool method."""
        if not self.connected:
            raise ConnectionError("Client not connected")
        
        # Return mock response
        return [{
            "text": f"Mock response for tool {name} with params {parameters or {}}"
        }]


# Custom assertions
def assert_tool_response_format(response):
    """
    Assert that a tool response has the correct format.
    
    Args:
        response: Tool response to validate
    """
    assert isinstance(response, dict), "Response must be a dictionary"
    assert "success" in response, "Response must have 'success' field"
    assert isinstance(response["success"], bool), "'success' must be boolean"
    
    if response["success"]:
        assert "data" in response, "Successful response must have 'data' field"
    else:
        assert "error" in response, "Failed response must have 'error' field"
        assert "error_code" in response, "Failed response must have 'error_code' field"


def assert_health_check_format(result):
    """
    Assert that a health check result has the correct format.
    
    Args:
        result: Health check result to validate
    """
    assert isinstance(result, dict), "Health check result must be a dictionary"
    assert "overall_status" in result, "Must have 'overall_status' field"
    assert result["overall_status"] in ["healthy", "warning", "unhealthy"], "Invalid overall status"
    assert "checks" in result, "Must have 'checks' field"
    assert isinstance(result["checks"], dict), "'checks' must be a dictionary"
    assert "execution_time" in result, "Must have 'execution_time' field"
    assert isinstance(result["execution_time"], (int, float)), "'execution_time' must be numeric" 