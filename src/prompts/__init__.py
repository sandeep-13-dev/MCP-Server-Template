"""
Prompts module for MCP Server Template.

This module handles loading and registration of all MCP prompts.
Add your prompt implementations to this package and register them here.
"""

import importlib
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

logger = logging.getLogger(__name__)


async def load_prompts(mcp: "FastMCP") -> int:
    """
    Load all prompts into the MCP server.
    
    This function dynamically imports and registers all prompt modules.
    Add new prompt modules to the PROMPT_MODULES list below.
    
    Args:
        mcp: The FastMCP server instance
        
    Returns:
        Number of prompts loaded
    """
    # List of prompt modules to load
    # Add your prompt modules here
    PROMPT_MODULES = [
        "prompts.example_prompts",
        # "prompts.code_generation",
        # "prompts.data_analysis",
        # Add more prompt modules as needed
    ]
    
    prompts_loaded = 0
    
    for module_name in PROMPT_MODULES:
        try:
            logger.debug(f"Loading prompt module: {module_name}")
            
            # Import the module - this will register its prompts with the MCP instance
            importlib.import_module(module_name)
            
            # Count would be handled by the prompt decorators in each module
            # For now, we'll assume each module adds at least one prompt
            prompts_loaded += 1
            
            logger.debug(f"Successfully loaded prompt module: {module_name}")
            
        except ImportError as e:
            logger.warning(f"Failed to import prompt module {module_name}: {e}")
        except Exception as e:
            logger.error(f"Error loading prompt module {module_name}: {e}")
            # Don't raise here - we want to continue loading other modules
    
    logger.info(f"Loaded {prompts_loaded} prompt modules")
    return prompts_loaded


# Re-export commonly used classes for convenience
from .example_prompts import *

__all__ = [
    "load_prompts",
] 