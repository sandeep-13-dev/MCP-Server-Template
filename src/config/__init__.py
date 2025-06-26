"""
Configuration module for MCP Server Template.

This module provides centralized configuration management with
environment variable support and validation.
"""

from .settings import settings, configure_logging

__all__ = [
    "settings",
    "configure_logging",
] 