# 📖 API Reference

Comprehensive reference for the MCP Server Template API, including tools, resources, prompts, and configuration options.

## 🌐 Server Endpoints

### Base URL Structure
```
http://localhost:8000/mcp
```

### Transport Types
- **HTTP**: `http://host:port/mcp`
- **SSE**: `http://host:port/sse`
- **STDIO**: Direct process communication

## 🛠️ Tools Reference

### Built-in Tools

#### `echo`
Simple echo tool for testing connectivity.

**Parameters:**
- `message` (string, required): Message to echo back

**Response:**
```json
{
  "success": true,
  "data": {
    "echoed_message": "Hello, World!"
  },
  "message": "Message echoed successfully",
  "timestamp": "2024-12-26T10:00:00Z",
  "tool_name": "echo"
}
```

**Example:**
```python
result = await client.call_tool("echo", {"message": "Hello, MCP!"})
```

#### `get_current_time`
Get current time in specified timezone.

**Parameters:**
- `timezone_name` (string, optional): Timezone name (default: "UTC")

**Response:**
```json
{
  "success": true,
  "data": {
    "current_time": "2024-12-26T10:00:00+00:00",
    "timezone": "UTC",
    "unix_timestamp": 1703592000.0,
    "formatted": "2024-12-26 10:00:00 UTC"
  },
  "message": "Current time retrieved for UTC"
}
```

#### `calculate_statistics`
Calculate basic statistics for a list of numbers.

**Parameters:**
- `numbers` (array of numbers, required): List of numbers to analyze
- `precision` (integer, optional): Decimal precision (default: 2, range: 0-10)

**Response:**
```json
{
  "success": true,
  "data": {
    "count": 5,
    "sum": 15.0,
    "mean": 3.0,
    "median": 3.0,
    "min": 1,
    "max": 5,
    "std_dev": 1.41,
    "variance": 2.0
  },
  "message": "Statistics calculated successfully",
  "precision": 2
}
```

**Errors:**
- `EMPTY_LIST`: Numbers list cannot be empty
- `INVALID_TYPE`: All items must be numbers
- `INVALID_PRECISION`: Precision must be between 0 and 10

#### `simulate_async_work`
Simulate asynchronous work with configurable duration.

**Parameters:**
- `duration` (float, optional): Work duration in seconds (default: 1.0, max: 30)
- `should_fail` (boolean, optional): Whether to simulate failure (default: false)
- `return_data` (string, optional): Data to return on success (default: "work completed")

**Response:**
```json
{
  "success": true,
  "data": {
    "result": "work completed",
    "execution_time": 1.003,
    "duration_requested": 1.0,
    "start_time": "2024-12-26T10:00:00Z",
    "end_time": "2024-12-26T10:00:01Z"
  }
}
```

**Errors:**
- `INVALID_DURATION`: Duration cannot be negative
- `DURATION_TOO_LONG`: Duration too long (max 30 seconds)
- `SIMULATED_FAILURE`: Simulated failure occurred

#### `unreliable_operation`
Operation with retry logic and configurable failure rate.

**Parameters:**
- `success_rate` (float, optional): Success probability (default: 0.7, range: 0.0-1.0)
- `data` (string, optional): Data to return (default: "operation result")

**Response:**
```json
{
  "success": true,
  "data": {
    "result": "operation result",
    "attempts": 2,
    "success_rate": 0.7,
    "final_attempt": true
  }
}
```

#### `process_json_data`
Process JSON data with various operations.

**Parameters:**
- `json_string` (string, required): JSON string to process
- `operation` (string, optional): Operation type (default: "validate")
  - `validate`: Validate JSON syntax
  - `format`: Format/prettify JSON
  - `minify`: Minify JSON
  - `extract`: Extract specific keys
- `filter_key` (string, optional): Key to filter by (for extract operation)
- `sort_by` (string, optional): Key to sort by

**Response:**
```json
{
  "success": true,
  "data": {
    "operation": "validate",
    "valid": true,
    "processed_data": {...},
    "size_bytes": 156,
    "keys_count": 3
  }
}
```

#### `health_check`
Check server health status.

**Parameters:** None

**Response:**
```json
{
  "status": "healthy",
  "server": "MCP Server Template",
  "version": "1.0.0",
  "timestamp": 1703592000.0,
  "initialized": true
}
```

## 📚 Resources Reference

### Built-in Resources

#### `template://readme`
README template for new projects.

**URI:** `template://readme`
**Content-Type:** `text/markdown`

#### `template://dockerfile`
Dockerfile template.

**URI:** `template://dockerfile`
**Content-Type:** `text/plain`

#### `template://gitignore`
Python .gitignore template.

**URI:** `template://gitignore`
**Content-Type:** `text/plain`

#### `config://example`
Example configuration file.

**URI:** `config://example`
**Content-Type:** `application/json`

#### `docs://api`
API documentation template.

**URI:** `docs://api`
**Content-Type:** `text/markdown`

## 💬 Prompts Reference

### Built-in Prompts

#### `code-review`
Generate code review prompt.

**Parameters:**
- `code` (string, required): Code to review
- `language` (string, optional): Programming language (default: "python")
- `focus_areas` (array of strings, optional): Specific areas to focus on

**Example:**
```python
prompt = await client.get_prompt("code-review", {
    "code": "def hello():\n    print('world')",
    "language": "python",
    "focus_areas": ["performance", "security"]
})
```

#### `data-analysis`
Generate data analysis prompt.

**Parameters:**
- `data_description` (string, required): Description of the dataset
- `analysis_goals` (array of strings, required): Analysis objectives
- `data_format` (string, optional): Data format (default: "CSV")

#### `api-documentation`
Generate API documentation prompt.

**Parameters:**
- `endpoint_name` (string, required): API endpoint name/path
- `method` (string, required): HTTP method
- `parameters` (object, required): Parameter descriptions
- `description` (string, required): Endpoint description

#### `bug-report`
Generate bug report prompt.

**Parameters:**
- `issue_description` (string, required): Brief issue description
- `steps_to_reproduce` (array of strings, required): Reproduction steps
- `expected_behavior` (string, required): Expected behavior
- `actual_behavior` (string, required): Actual behavior
- `environment_info` (object, optional): Environment details

#### `feature-planning`
Generate feature planning prompt.

**Parameters:**
- `feature_name` (string, required): Feature name
- `feature_description` (string, required): Feature description
- `user_stories` (array of strings, required): User stories
- `constraints` (array of strings, optional): Development constraints

## ⚙️ Configuration Reference

### Environment Variables

#### Server Configuration
- `MCP_SERVER_NAME` (string): Server display name (default: "MCP Server Template")
- `MCP_SERVER_VERSION` (string): Server version (default: "1.0.0")
- `MCP_SERVER_DESCRIPTION` (string): Server description

#### Network Configuration
- `MCP_HOST` (string): Bind address (default: "0.0.0.0")
- `MCP_PORT` (integer): Server port (default: 8000, range: 1-65535)
- `MCP_TRANSPORT` (string): Transport type (default: "http", options: "http", "sse", "stdio")

#### Feature Flags
- `ENABLE_HEALTH_CHECK` (boolean): Enable health endpoints (default: true)
- `ENABLE_METRICS` (boolean): Enable metrics collection (default: false)
- `ENABLE_CORS` (boolean): Enable CORS (default: true)
- `ENABLE_LOGGING` (boolean): Enable logging (default: true)

#### Security Configuration
- `API_KEY` (string): API key for authentication (optional)
- `REQUIRE_AUTH` (boolean): Require authentication (auto-set if API_KEY provided)
- `CORS_ORIGINS` (string): Comma-separated allowed origins (default: "*")
- `CORS_METHODS` (string): Comma-separated allowed methods (default: "GET,POST,PUT,DELETE")

#### Logging Configuration
- `LOG_LEVEL` (string): Log level (default: "INFO", options: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
- `LOG_FORMAT` (string): Log format string
- `LOG_FILE` (string): Log file path (optional)

#### Performance Configuration
- `MAX_WORKERS` (integer): Maximum worker threads (default: 4, min: 1)
- `TIMEOUT_SECONDS` (integer): Request timeout (default: 30)
- `MAX_REQUEST_SIZE` (integer): Maximum request size in bytes (default: 1048576)

#### Development Configuration
- `DEBUG` (boolean): Enable debug mode (default: false)
- `RELOAD` (boolean): Enable auto-reload (default: false)
- `ENVIRONMENT` (string): Environment name (default: "production", options: "development", "testing", "production")

#### Database Configuration
- `DATABASE_URL` (string): Database connection URL (optional)
- `REDIS_URL` (string): Redis connection URL (optional)

### Settings Class Properties

#### Computed Properties
- `is_development`: Returns true if in development mode
- `is_production`: Returns true if in production mode  
- `log_level_int`: Returns log level as integer
- `server_url`: Returns full server URL
- `mcp_endpoint`: Returns MCP endpoint URL

#### Validation Methods
- `validate()`: Validates all configuration settings
- `to_dict()`: Returns settings as dictionary (excluding sensitive data)

## 🔧 Custom Tool Development

### Tool Decorator

```python
@mcp.tool
async def my_tool(param1: str, param2: int = 10) -> Dict[str, Any]:
    """Tool description."""
    return {"result": "success"}
```

### Tool Base Classes

```python
from tools.base import BaseTool, ToolError

class MyTool(BaseTool):
    async def execute(self, **kwargs) -> Dict[str, Any]:
        return {"result": "success"}
```

### Tool Utilities

#### Decorators
- `@validate_required_params(*params)`: Validate required parameters
- `@tool_timeout(seconds)`: Add timeout to tool execution
- `@tool_retry(max_attempts, delay, backoff)`: Add retry logic

#### Helper Functions
- `format_success_response(data, message, **metadata)`: Format success response
- `format_error_response(error, error_code, **metadata)`: Format error response

#### Exception Classes
- `ToolError(message, code, retry=False)`: Tool-specific error

## 📊 Monitoring Endpoints

### Health Check
**Endpoint:** `GET /health`
**Description:** Basic health check endpoint

### Metrics
**Endpoint:** `GET /metrics`
**Description:** Prometheus metrics (if enabled)

### Server Info
**Endpoint:** `GET /info`
**Description:** Server information and statistics

## 🔌 Client Integration

### FastMCP Client

```python
from fastmcp import Client

# HTTP transport
client = Client("http://localhost:8000/mcp")

# With authentication
client = Client("http://localhost:8000/mcp", headers={
    "X-API-Key": "your-api-key"
})
```

### Available Client Methods

- `await client.list_tools()`: List available tools
- `await client.list_resources()`: List available resources
- `await client.list_prompts()`: List available prompts
- `await client.call_tool(name, params)`: Call a tool
- `await client.read_resource(uri)`: Read a resource
- `await client.get_prompt(name, params)`: Get a prompt
- `await client.ping()`: Ping the server

## 🚨 Error Handling

### Standard Error Format

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-12-26T10:00:00Z",
  "tool_name": "tool_name"
}
```

### Common Error Codes

- `MISSING_PARAMETER`: Required parameter not provided
- `INVALID_PARAMETER`: Parameter value is invalid
- `TIMEOUT_ERROR`: Operation timed out
- `RATE_LIMITED`: Rate limit exceeded
- `SERVER_ERROR`: Internal server error
- `NOT_FOUND`: Resource not found
- `UNAUTHORIZED`: Authentication required

### HTTP Status Codes

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (authentication required)
- `404`: Not Found (tool/resource not found)
- `405`: Method Not Allowed
- `429`: Too Many Requests (rate limited)
- `500`: Internal Server Error
- `503`: Service Unavailable

---

This API reference provides complete documentation for all available endpoints, tools, resources, and configuration options in the MCP Server Template. 