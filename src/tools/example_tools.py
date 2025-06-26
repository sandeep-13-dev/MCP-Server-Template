"""
Example tools for MCP Server Template.

This module demonstrates various patterns for creating MCP tools:
- Simple tools with basic parameters
- Tools with complex validation
- Tools with async operations
- Tools with error handling
- Tools with retry logic and timeouts
"""

import asyncio
import json
import random
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from fastmcp import FastMCP
from .base import (
    BaseTool, ToolResult, ToolError,
    tool_timeout, tool_retry, validate_required_params,
    format_success_response, format_error_response
)

# Get the global FastMCP instance
# In your actual implementation, you'll need to manage this properly
mcp = FastMCP("MCP Server Template")


# =============================================================================
# Simple Tools
# =============================================================================

@mcp.tool
async def echo(message: str) -> Dict[str, Any]:
    """
    Echo a message back to the caller.
    
    A simple example tool that demonstrates basic MCP tool structure.
    
    Args:
        message: The message to echo back
        
    Returns:
        Dict containing the echoed message and metadata
    """
    return format_success_response(
        data={"echoed_message": message},
        message="Message echoed successfully",
        timestamp=datetime.now(timezone.utc).isoformat(),
        tool_name="echo"
    )


@mcp.tool
async def get_current_time(timezone_name: str = "UTC") -> Dict[str, Any]:
    """
    Get the current time in the specified timezone.
    
    Args:
        timezone_name: Timezone name (e.g., "UTC", "US/Eastern")
        
    Returns:
        Dict containing current time information
    """
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(timezone_name)
        current_time = datetime.now(tz)
        
        return format_success_response(
            data={
                "current_time": current_time.isoformat(),
                "timezone": timezone_name,
                "unix_timestamp": current_time.timestamp(),
                "formatted": current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            },
            message=f"Current time retrieved for {timezone_name}"
        )
        
    except Exception as e:
        return format_error_response(
            error=f"Invalid timezone: {timezone_name}",
            error_code="INVALID_TIMEZONE",
            available_timezones="Use standard timezone names like UTC, US/Eastern, Europe/London"
        )


# =============================================================================
# Tools with Validation
# =============================================================================

@mcp.tool
@validate_required_params("numbers")
async def calculate_statistics(numbers: List[float], precision: int = 2) -> Dict[str, Any]:
    """
    Calculate basic statistics for a list of numbers.
    
    Demonstrates parameter validation and error handling.
    
    Args:
        numbers: List of numbers to analyze
        precision: Decimal precision for results (default: 2)
        
    Returns:
        Dict containing statistical analysis
    """
    try:
        if not numbers:
            raise ToolError("Numbers list cannot be empty", "EMPTY_LIST")
        
        if not all(isinstance(n, (int, float)) for n in numbers):
            raise ToolError("All items must be numbers", "INVALID_TYPE")
        
        if precision < 0 or precision > 10:
            raise ToolError("Precision must be between 0 and 10", "INVALID_PRECISION")
        
        # Calculate statistics
        count = len(numbers)
        total = sum(numbers)
        mean = total / count
        sorted_nums = sorted(numbers)
        
        # Median
        mid = count // 2
        if count % 2 == 0:
            median = (sorted_nums[mid - 1] + sorted_nums[mid]) / 2
        else:
            median = sorted_nums[mid]
        
        # Standard deviation
        variance = sum((x - mean) ** 2 for x in numbers) / count
        std_dev = variance ** 0.5
        
        stats = {
            "count": count,
            "sum": round(total, precision),
            "mean": round(mean, precision),
            "median": round(median, precision),
            "min": min(numbers),
            "max": max(numbers),
            "std_dev": round(std_dev, precision),
            "variance": round(variance, precision)
        }
        
        return format_success_response(
            data=stats,
            message="Statistics calculated successfully",
            precision=precision
        )
        
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Calculation error: {str(e)}", "CALCULATION_ERROR")


# =============================================================================
# Async Tools with Timeout
# =============================================================================

@mcp.tool
@tool_timeout(10)  # 10 second timeout
async def simulate_async_work(
    duration: float = 1.0, 
    should_fail: bool = False,
    return_data: str = "work completed"
) -> Dict[str, Any]:
    """
    Simulate asynchronous work with configurable duration and failure.
    
    Demonstrates async operations, timeouts, and error simulation.
    
    Args:
        duration: How long to simulate work (seconds)
        should_fail: Whether to simulate a failure
        return_data: Data to return on success
        
    Returns:
        Dict containing work results
    """
    if duration < 0:
        raise ToolError("Duration cannot be negative", "INVALID_DURATION")
    
    if duration > 30:
        raise ToolError("Duration too long (max 30 seconds)", "DURATION_TOO_LONG")
    
    start_time = time.time()
    
    # Simulate work
    await asyncio.sleep(duration)
    
    if should_fail:
        raise ToolError("Simulated failure occurred", "SIMULATED_FAILURE")
    
    execution_time = time.time() - start_time
    
    return format_success_response(
        data={
            "result": return_data,
            "requested_duration": duration,
            "actual_duration": round(execution_time, 3),
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        message="Async work completed successfully"
    )


# =============================================================================
# Tools with Retry Logic
# =============================================================================

@mcp.tool
@tool_retry(max_attempts=3, delay=0.5, backoff=2.0)
async def unreliable_operation(
    success_rate: float = 0.7,
    data: str = "operation result"
) -> Dict[str, Any]:
    """
    Simulate an unreliable operation that sometimes fails.
    
    Demonstrates retry logic and probabilistic failures.
    
    Args:
        success_rate: Probability of success (0.0 to 1.0)
        data: Data to return on success
        
    Returns:
        Dict containing operation results
    """
    if not 0.0 <= success_rate <= 1.0:
        raise ToolError("Success rate must be between 0.0 and 1.0", "INVALID_RATE")
    
    # Simulate random failure
    if random.random() > success_rate:
        raise ToolError("Random failure occurred", "RANDOM_FAILURE")
    
    return format_success_response(
        data={"result": data},
        message="Unreliable operation succeeded",
        success_rate=success_rate,
        attempt_time=datetime.now(timezone.utc).isoformat()
    )


# =============================================================================
# Complex Data Processing Tools
# =============================================================================

@mcp.tool
async def process_json_data(
    json_string: str,
    operation: str = "validate",
    filter_key: Optional[str] = None,
    sort_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process JSON data with various operations.
    
    Demonstrates complex data processing and multiple operation modes.
    
    Args:
        json_string: JSON string to process
        operation: Operation to perform (validate, filter, sort, transform)
        filter_key: Key to filter by (for filter operation)
        sort_by: Key to sort by (for sort operation)
        
    Returns:
        Dict containing processed data
    """
    try:
        # Parse JSON
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ToolError(f"Invalid JSON: {str(e)}", "INVALID_JSON")
        
        result = {"original_data": data}
        
        if operation == "validate":
            result["validation"] = {
                "valid": True,
                "type": type(data).__name__,
                "size": len(str(data))
            }
            
        elif operation == "filter" and filter_key:
            if isinstance(data, list):
                filtered = [item for item in data if isinstance(item, dict) and filter_key in item]
                result["filtered_data"] = filtered
                result["filter_stats"] = {"original_count": len(data), "filtered_count": len(filtered)}
            else:
                raise ToolError("Filtering requires array data", "INVALID_DATA_TYPE")
                
        elif operation == "sort" and sort_by:
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                try:
                    sorted_data = sorted(data, key=lambda x: x.get(sort_by, ""))
                    result["sorted_data"] = sorted_data
                    result["sort_key"] = sort_by
                except Exception as e:
                    raise ToolError(f"Sort failed: {str(e)}", "SORT_ERROR")
            else:
                raise ToolError("Sorting requires array of objects", "INVALID_DATA_TYPE")
                
        elif operation == "transform":
            # Simple transformation example
            if isinstance(data, dict):
                transformed = {k: str(v).upper() if isinstance(v, str) else v for k, v in data.items()}
                result["transformed_data"] = transformed
            elif isinstance(data, list):
                transformed = [str(item).upper() if isinstance(item, str) else item for item in data]
                result["transformed_data"] = transformed
            else:
                result["transformed_data"] = str(data).upper()
                
        else:
            raise ToolError(f"Unknown operation: {operation}", "UNKNOWN_OPERATION")
        
        return format_success_response(
            data=result,
            message=f"JSON {operation} completed successfully",
            operation=operation
        )
        
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Processing error: {str(e)}", "PROCESSING_ERROR")


# =============================================================================
# File-like Operations (simulated)
# =============================================================================

@mcp.tool
async def generate_report(
    title: str,
    data: Dict[str, Any],
    format_type: str = "json",
    include_timestamp: bool = True
) -> Dict[str, Any]:
    """
    Generate a formatted report from data.
    
    Demonstrates data formatting and report generation patterns.
    
    Args:
        title: Report title
        data: Data to include in report
        format_type: Report format (json, text, markdown)
        include_timestamp: Whether to include timestamp
        
    Returns:
        Dict containing generated report
    """
    if not title.strip():
        raise ToolError("Title cannot be empty", "EMPTY_TITLE")
    
    if format_type not in ["json", "text", "markdown"]:
        raise ToolError("Format must be json, text, or markdown", "INVALID_FORMAT")
    
    timestamp = datetime.now(timezone.utc).isoformat() if include_timestamp else None
    
    if format_type == "json":
        report = {
            "title": title,
            "data": data,
            "generated_at": timestamp,
            "format": "json"
        }
        content = json.dumps(report, indent=2)
        
    elif format_type == "text":
        lines = [f"Report: {title}"]
        if timestamp:
            lines.append(f"Generated: {timestamp}")
        lines.append("-" * 50)
        lines.append(f"Data: {json.dumps(data, indent=2)}")
        content = "\n".join(lines)
        
    elif format_type == "markdown":
        lines = [f"# {title}"]
        if timestamp:
            lines.append(f"*Generated: {timestamp}*")
        lines.append("\n## Data\n")
        lines.append(f"```json\n{json.dumps(data, indent=2)}\n```")
        content = "\n".join(lines)
    
    return format_success_response(
        data={
            "report_content": content,
            "title": title,
            "format": format_type,
            "size": len(content),
            "generated_at": timestamp
        },
        message="Report generated successfully"
    )


# =============================================================================
# Health and Monitoring Tools
# =============================================================================

@mcp.tool
async def system_health_check() -> Dict[str, Any]:
    """
    Perform a basic system health check.
    
    Demonstrates health monitoring patterns.
    
    Returns:
        Dict containing system health information
    """
    import sys
    import psutil
    
    try:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_data = {
            "python_version": sys.version,
            "cpu_usage_percent": cpu_percent,
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "usage_percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": round((disk.used / disk.total) * 100, 2)
            },
            "status": "healthy" if cpu_percent < 90 and memory.percent < 90 else "warning"
        }
        
        return format_success_response(
            data=health_data,
            message="Health check completed",
            check_time=datetime.now(timezone.utc).isoformat()
        )
        
    except ImportError:
        return format_error_response(
            error="psutil not available - install it for system monitoring",
            error_code="DEPENDENCY_MISSING",
            suggestion="pip install psutil"
        )
    except Exception as e:
        raise ToolError(f"Health check failed: {str(e)}", "HEALTH_CHECK_ERROR")


# Export all tools for the module loader
__all__ = [
    "echo",
    "get_current_time", 
    "calculate_statistics",
    "simulate_async_work",
    "unreliable_operation", 
    "process_json_data",
    "generate_report",
    "system_health_check"
] 