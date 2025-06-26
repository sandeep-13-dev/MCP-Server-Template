# 🧮 Basic Calculator Example

A simple calculator implementation demonstrating basic tool development patterns with the MCP Server Template.

## Overview

This example implements basic arithmetic operations (addition, subtraction, multiplication, division) as MCP tools, showcasing:
- Parameter validation
- Error handling
- Type safety
- Documentation patterns

## Implementation

### Tool Implementation

```python
# src/tools/calculator_tools.py
from fastmcp import FastMCP
from typing import Dict, Any, Union
from .base import ToolError, format_success_response, format_error_response

mcp = FastMCP("Calculator Server")

@mcp.tool
async def add(a: float, b: float) -> Dict[str, Any]:
    """
    Add two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Dict containing the sum
    """
    result = a + b
    return format_success_response(
        data={
            "result": result,
            "operation": "addition",
            "operands": [a, b]
        },
        message=f"Successfully calculated {a} + {b} = {result}"
    )

@mcp.tool
async def subtract(a: float, b: float) -> Dict[str, Any]:
    """
    Subtract second number from first number.
    
    Args:
        a: First number (minuend)
        b: Second number (subtrahend)
        
    Returns:
        Dict containing the difference
    """
    result = a - b
    return format_success_response(
        data={
            "result": result,
            "operation": "subtraction", 
            "operands": [a, b]
        },
        message=f"Successfully calculated {a} - {b} = {result}"
    )

@mcp.tool
async def multiply(a: float, b: float) -> Dict[str, Any]:
    """
    Multiply two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Dict containing the product
    """
    result = a * b
    return format_success_response(
        data={
            "result": result,
            "operation": "multiplication",
            "operands": [a, b]
        },
        message=f"Successfully calculated {a} × {b} = {result}"
    )

@mcp.tool
async def divide(a: float, b: float) -> Dict[str, Any]:
    """
    Divide first number by second number.
    
    Args:
        a: Dividend
        b: Divisor
        
    Returns:
        Dict containing the quotient
        
    Raises:
        ToolError: If division by zero is attempted
    """
    if b == 0:
        raise ToolError("Cannot divide by zero", "DIVISION_BY_ZERO")
    
    result = a / b
    return format_success_response(
        data={
            "result": result,
            "operation": "division",
            "operands": [a, b]
        },
        message=f"Successfully calculated {a} ÷ {b} = {result}"
    )

@mcp.tool
async def calculate_expression(expression: str) -> Dict[str, Any]:
    """
    Evaluate a mathematical expression safely.
    
    Args:
        expression: Mathematical expression (e.g., "2 + 3 * 4")
        
    Returns:
        Dict containing the result
        
    Raises:
        ToolError: If expression is invalid or unsafe
    """
    # Basic security: only allow numbers, operators, and parentheses
    import re
    if not re.match(r'^[0-9+\-*/().\s]+$', expression):
        raise ToolError("Invalid characters in expression", "INVALID_EXPRESSION")
    
    try:
        # Safe evaluation using eval (restricted input)
        result = eval(expression)
        return format_success_response(
            data={
                "result": result,
                "expression": expression,
                "operation": "expression_evaluation"
            },
            message=f"Successfully evaluated: {expression} = {result}"
        )
    except ZeroDivisionError:
        raise ToolError("Division by zero in expression", "DIVISION_BY_ZERO")
    except Exception as e:
        raise ToolError(f"Invalid expression: {str(e)}", "EVALUATION_ERROR")
```

### Registration

Add to `src/tools/__init__.py`:

```python
TOOL_MODULES = [
    "tools.example_tools",
    "tools.calculator_tools",  # Add this line
]
```

## Usage Examples

### Python Client

```python
# test_calculator.py
import asyncio
import json
from fastmcp import Client

async def test_calculator():
    client = Client("http://localhost:8000/mcp")
    
    async with client:
        # Basic arithmetic
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"5 + 3 = {json.loads(result[0].text)['data']['result']}")
        
        result = await client.call_tool("multiply", {"a": 7, "b": 6})
        print(f"7 × 6 = {json.loads(result[0].text)['data']['result']}")
        
        # Division with error handling
        try:
            result = await client.call_tool("divide", {"a": 10, "b": 0})
        except Exception as e:
            print(f"Division by zero caught: {e}")
        
        # Expression evaluation
        result = await client.call_tool("calculate_expression", {
            "expression": "2 + 3 * 4"
        })
        data = json.loads(result[0].text)
        print(f"2 + 3 * 4 = {data['data']['result']}")

if __name__ == "__main__":
    asyncio.run(test_calculator())
```

### cURL Examples

```bash
# Addition
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "add", "arguments": {"a": 5, "b": 3}}}'

# Expression evaluation
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "calculate_expression", "arguments": {"expression": "10 + 20 * 3"}}}'
```

## Testing

```python
# tests/test_calculator.py
import pytest
import json
from fastmcp import Client
from src.server import create_server

class TestCalculator:
    @pytest.fixture
    async def client(self):
        server = create_server()
        client = Client(server)
        async with client:
            yield client
    
    async def test_add(self, client):
        result = await client.call_tool("add", {"a": 5, "b": 3})
        data = json.loads(result[0].text)
        assert data["success"] is True
        assert data["data"]["result"] == 8
        assert data["data"]["operation"] == "addition"
    
    async def test_divide_by_zero(self, client):
        with pytest.raises(Exception):
            await client.call_tool("divide", {"a": 10, "b": 0})
    
    async def test_expression_evaluation(self, client):
        result = await client.call_tool("calculate_expression", {
            "expression": "2 + 3 * 4"
        })
        data = json.loads(result[0].text)
        assert data["data"]["result"] == 14
    
    async def test_invalid_expression(self, client):
        with pytest.raises(Exception):
            await client.call_tool("calculate_expression", {
                "expression": "import os; os.system('ls')"
            })
```

## Setup Instructions

1. **Add the calculator tools**:
   ```bash
   # Copy the calculator_tools.py to your tools directory
   cp docs/examples/basic-calculator/calculator_tools.py src/tools/
   ```

2. **Update tool registration**:
   ```python
   # Edit src/tools/__init__.py
   TOOL_MODULES = [
       "tools.example_tools",
       "tools.calculator_tools",
   ]
   ```

3. **Start the server**:
   ```bash
   python src/server.py
   ```

4. **Test the tools**:
   ```bash
   python docs/examples/basic-calculator/test_calculator.py
   ```

## Key Concepts Demonstrated

### 1. Type Safety
- Using Python type hints for parameters
- Clear parameter documentation
- Consistent return types

### 2. Error Handling
- Custom `ToolError` exceptions
- Meaningful error messages and codes
- Graceful handling of edge cases

### 3. Response Formatting
- Consistent response structure
- Helpful metadata inclusion
- Standard success/error patterns

### 4. Security Considerations
- Input validation for expression evaluation
- Safe evaluation practices
- Protection against code injection

## Next Steps

- **Add more operations**: Power, square root, logarithms
- **Add memory functions**: Store and recall values
- **Add unit conversions**: Temperature, distance, weight
- **Add complex numbers**: Support for imaginary numbers
- **Add expression history**: Track previous calculations

This example provides a solid foundation for building more complex mathematical tools and demonstrates best practices for MCP tool development. 