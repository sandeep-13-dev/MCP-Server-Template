"""
Resources module for MCP Server Template.

This module handles loading and registration of all MCP resources.
Add your resource implementations to this package and register them here.
"""

import importlib
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

logger = logging.getLogger(__name__)


async def load_resources(mcp: "FastMCP") -> int:
    """
    Load all resources into the MCP server.
    
    This function dynamically imports and registers all resource modules.
    Add new resource modules to the RESOURCE_MODULES list below.
    
    Args:
        mcp: The FastMCP server instance
        
    Returns:
        Number of resources loaded
    """
    # List of resource modules to load
    # Add your resource modules here
    RESOURCE_MODULES = [
        "resources.example_resources",
        # "resources.file_resources",
        # "resources.database_resources",
        # Add more resource modules as needed
    ]
    
    resources_loaded = 0
    
    for module_name in RESOURCE_MODULES:
        try:
            logger.debug(f"Loading resource module: {module_name}")
            
            # Import the module - this will register its resources with the MCP instance
            importlib.import_module(module_name)
            
            # Count would be handled by the resource decorators in each module
            # For now, we'll assume each module adds at least one resource
            resources_loaded += 1
            
            logger.debug(f"Successfully loaded resource module: {module_name}")
            
        except ImportError as e:
            logger.warning(f"Failed to import resource module {module_name}: {e}")
        except Exception as e:
            logger.error(f"Error loading resource module {module_name}: {e}")
            # Don't raise here - we want to continue loading other modules
    
    logger.info(f"Loaded {resources_loaded} resource modules")
    return resources_loaded


# Re-export commonly used classes for convenience
from .example_resources import *

__all__ = [
    "load_resources",
] 