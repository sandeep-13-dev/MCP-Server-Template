"""
Base classes and utilities for MCP tools.

Provides common functionality and patterns for tool development.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Generic
from dataclasses import dataclass
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ToolError(Exception):
    """Base exception for tool-related errors."""
    
    def __init__(self, message: str, error_code: str = "TOOL_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


@dataclass
class ToolResult(Generic[T]):
    """Standardized tool result format."""
    
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        result = {
            "success": self.success,
            "execution_time": self.execution_time
        }
        
        if self.success:
            result["data"] = self.data
            if self.metadata:
                result["metadata"] = self.metadata
        else:
            result["error"] = self.error
            if self.error_code:
                result["error_code"] = self.error_code
        
        return result


class BaseTool(ABC):
    """
    Abstract base class for MCP tools.
    
    Provides common functionality like error handling, logging, and result formatting.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize the tool.
        
        Args:
            name: Tool name (should be unique)
            description: Tool description for MCP clients
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters.
        
        This method should be implemented by subclasses.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult with success/failure status and data
        """
        pass
    
    async def __call__(self, **kwargs) -> Dict[str, Any]:
        """
        Call the tool and return standardized result.
        
        This wrapper handles common concerns like timing, error handling, and logging.
        """
        start_time = time.time()
        
        try:
            self.logger.debug(f"Executing tool {self.name} with args: {kwargs}")
            
            # Validate parameters
            await self.validate_parameters(**kwargs)
            
            # Execute the tool
            result = await self.execute(**kwargs)
            
            # Add execution time
            result.execution_time = time.time() - start_time
            
            self.logger.debug(f"Tool {self.name} completed in {result.execution_time:.3f}s")
            
            return result.to_dict()
            
        except ToolError as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Tool {self.name} failed: {e.message}")
            
            return ToolResult(
                success=False,
                error=e.message,
                error_code=e.error_code,
                execution_time=execution_time,
                metadata=e.details
            ).to_dict()
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.exception(f"Unexpected error in tool {self.name}")
            
            return ToolResult(
                success=False,
                error=str(e),
                error_code="UNEXPECTED_ERROR",
                execution_time=execution_time
            ).to_dict()
    
    async def validate_parameters(self, **kwargs) -> None:
        """
        Validate tool parameters.
        
        Override this method to add custom parameter validation.
        
        Args:
            **kwargs: Tool parameters
            
        Raises:
            ToolError: If parameters are invalid
        """
        pass


def tool_timeout(seconds: int):
    """
    Decorator to add timeout to tool functions.
    
    Args:
        seconds: Timeout in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                raise ToolError(
                    f"Tool execution timed out after {seconds} seconds",
                    error_code="TIMEOUT_ERROR"
                )
        return wrapper
    return decorator


def tool_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to add retry logic to tool functions.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Backoff multiplier for delay
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Tool attempt {attempt + 1} failed, retrying in {current_delay}s: {e}")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"Tool failed after {max_attempts} attempts")
            
            # Re-raise the last exception
            raise last_exception
        return wrapper
    return decorator


def validate_required_params(*required_params):
    """
    Decorator to validate required parameters for tool functions.
    
    Args:
        *required_params: List of required parameter names
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            missing_params = [param for param in required_params if param not in kwargs]
            if missing_params:
                raise ToolError(
                    f"Missing required parameters: {', '.join(missing_params)}",
                    error_code="MISSING_PARAMETERS",
                    details={"missing_parameters": missing_params}
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Utility functions for common tool patterns

async def safe_execute(coro, default_value=None, error_message="Operation failed"):
    """
    Safely execute a coroutine with error handling.
    
    Args:
        coro: Coroutine to execute
        default_value: Value to return on error
        error_message: Error message prefix
        
    Returns:
        Result of coroutine or default_value on error
    """
    try:
        return await coro
    except Exception as e:
        logger.error(f"{error_message}: {e}")
        return default_value


def format_success_response(data: Any, message: str = "Operation completed successfully", **metadata) -> Dict[str, Any]:
    """
    Format a successful tool response.
    
    Args:
        data: Response data
        message: Success message
        **metadata: Additional metadata
        
    Returns:
        Formatted response dictionary
    """
    return {
        "success": True,
        "message": message,
        "data": data,
        "metadata": metadata
    }


def format_error_response(error: str, error_code: str = "ERROR", **details) -> Dict[str, Any]:
    """
    Format an error tool response.
    
    Args:
        error: Error message
        error_code: Error code
        **details: Additional error details
        
    Returns:
        Formatted error response dictionary
    """
    return {
        "success": False,
        "error": error,
        "error_code": error_code,
        "details": details
    } 