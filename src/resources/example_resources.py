"""
Example resources for MCP Server Template.

This module demonstrates how to create MCP resources that provide
templates, documents, and other content to MCP clients.
"""

from fastmcp import FastMCP
from typing import Dict, Any, List

# Get the global FastMCP instance
mcp = FastMCP("MCP Server Template")


@mcp.resource("template://readme")
async def readme_template() -> str:
    """
    Provide a README template for new projects.
    
    Returns:
        String containing README template content
    """
    return """# Project Name

## Description
Brief description of your project.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from your_project import main
main()
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
MIT License
"""


@mcp.resource("template://dockerfile")
async def dockerfile_template() -> str:
    """
    Provide a Dockerfile template.
    
    Returns:
        String containing Dockerfile template content
    """
    return """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
"""


@mcp.resource("template://gitignore")
async def gitignore_template() -> str:
    """
    Provide a Python .gitignore template.
    
    Returns:
        String containing .gitignore template content
    """
    return """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""


@mcp.resource("config://example")
async def example_config() -> str:
    """
    Provide an example configuration file.
    
    Returns:
        String containing example configuration content
    """
    return """{
  "server": {
    "host": "localhost",
    "port": 8000,
    "debug": false
  },
  "database": {
    "url": "sqlite:///app.db",
    "echo": false
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
"""


@mcp.resource("docs://api")
async def api_documentation() -> str:
    """
    Provide API documentation.
    
    Returns:
        String containing API documentation
    """
    return """# API Documentation

## Overview
This API provides tools for data processing and analysis.

## Authentication
Include your API key in the header:
```
X-API-Key: your-api-key-here
```

## Endpoints

### GET /tools
List all available tools.

**Response:**
```json
{
  "tools": [
    {
      "name": "process_data",
      "description": "Process data with various operations"
    }
  ]
}
```

### POST /tools/{tool_name}
Execute a specific tool.

**Parameters:**
- `tool_name`: Name of the tool to execute

**Request Body:**
```json
{
  "parameters": {
    "data": "input data",
    "operation": "transform"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "result": "processed data"
  },
  "execution_time": 0.123
}
```

## Error Handling
All errors return a standardized format:

```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_CODE",
  "details": {}
}
```

## Rate Limiting
API calls are limited to 1000 requests per hour per API key.
"""


# Export all resources for the module loader
__all__ = [
    "readme_template",
    "dockerfile_template", 
    "gitignore_template",
    "example_config",
    "api_documentation"
] 