"""
Tools module for MCP Server Template.

This module handles loading and registration of all MCP tools.
Add your tool implementations to this package and register them here.
"""

import importlib
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

logger = logging.getLogger(__name__)


async def load_tools(mcp: "FastMCP") -> int:
    """
    Load all tools into the MCP server.
    
    This function dynamically imports and registers all tool modules.
    Add new tool modules to the TOOL_MODULES list below.
    
    Args:
        mcp: The FastMCP server instance
        
    Returns:
        Number of tools loaded
    """
    # List of tool modules to load
    # Add your tool modules here
    TOOL_MODULES = [
        "tools.example_tools",
        # "tools.data_processing",
        # "tools.file_operations", 
        # "tools.api_integrations",
        # Add more tool modules as needed
    ]
    
    tools_loaded = 0
    
    for module_name in TOOL_MODULES:
        try:
            logger.debug(f"Loading tool module: {module_name}")
            
            # Import the module - this will register its tools with the MCP instance
            importlib.import_module(module_name)
            
            # Count would be handled by the tool decorators in each module
            # For now, we'll assume each module adds at least one tool
            tools_loaded += 1
            
            logger.debug(f"Successfully loaded tool module: {module_name}")
            
        except ImportError as e:
            logger.warning(f"Failed to import tool module {module_name}: {e}")
        except Exception as e:
            logger.error(f"Error loading tool module {module_name}: {e}")
            # Don't raise here - we want to continue loading other modules
    
    logger.info(f"Loaded {tools_loaded} tool modules")
    return tools_loaded


# Re-export commonly used classes and functions for convenience
from .base import BaseTool, ToolError
from .example_tools import *

__all__ = [
    "load_tools",
    "BaseTool", 
    "ToolError",
] 