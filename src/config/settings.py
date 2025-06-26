"""
Configuration management for MCP Server Template.

Handles environment variables, defaults, and settings validation.
All configuration is centralized here for easy maintenance and testing.
"""

import os
import logging
from typing import Optional, List
from pathlib import Path


class Settings:
    """Application settings with environment variable support."""
    
    # =========================================================================
    # Server Configuration
    # =========================================================================
    
    SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "MCP Server Template")
    SERVER_VERSION: str = os.getenv("MCP_SERVER_VERSION", "1.0.0")
    SERVER_DESCRIPTION: str = os.getenv(
        "MCP_SERVER_DESCRIPTION", 
        "A robust template for building FastMCP servers"
    )
    
    # =========================================================================
    # Network Configuration
    # =========================================================================
    
    HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("MCP_PORT", "8000"))
    TRANSPORT: str = os.getenv("MCP_TRANSPORT", "http").lower()
    
    # =========================================================================
    # Feature Flags
    # =========================================================================
    
    ENABLE_HEALTH_CHECK: bool = os.getenv("ENABLE_HEALTH_CHECK", "true").lower() == "true"
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "true").lower() == "true"
    ENABLE_LOGGING: bool = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
    
    # =========================================================================
    # Security Configuration
    # =========================================================================
    
    API_KEY: Optional[str] = os.getenv("API_KEY")
    REQUIRE_AUTH: bool = API_KEY is not None
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_METHODS: List[str] = os.getenv("CORS_METHODS", "GET,POST,PUT,DELETE").split(",")
    
    # =========================================================================
    # Logging Configuration
    # =========================================================================
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT", 
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # =========================================================================
    # Performance Configuration
    # =========================================================================
    
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    TIMEOUT_SECONDS: int = int(os.getenv("TIMEOUT_SECONDS", "30"))
    MAX_REQUEST_SIZE: int = int(os.getenv("MAX_REQUEST_SIZE", "1048576"))  # 1MB
    
    # =========================================================================
    # Development Configuration
    # =========================================================================
    
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production").lower()
    
    # =========================================================================
    # Database Configuration (if needed)
    # =========================================================================
    
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # =========================================================================
    # External Services Configuration
    # =========================================================================
    
    # Add your external service configurations here
    # Example:
    # OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    # ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # =========================================================================
    # Validation and Computed Properties
    # =========================================================================
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development" or self.DEBUG
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production" and not self.DEBUG
    
    @property
    def log_level_int(self) -> int:
        """Get log level as integer."""
        return getattr(logging, self.LOG_LEVEL, logging.INFO)
    
    @property
    def server_url(self) -> str:
        """Get the full server URL."""
        protocol = "http" if not self.API_KEY else "https"
        return f"{protocol}://{self.HOST}:{self.PORT}"
    
    @property
    def mcp_endpoint(self) -> str:
        """Get the MCP endpoint URL."""
        return f"{self.server_url}/mcp"
    
    def validate(self) -> None:
        """Validate configuration settings."""
        errors = []
        
        # Validate transport
        valid_transports = ["http", "sse", "stdio"]
        if self.TRANSPORT not in valid_transports:
            errors.append(f"Invalid transport: {self.TRANSPORT}. Must be one of {valid_transports}")
        
        # Validate port
        if not (1 <= self.PORT <= 65535):
            errors.append(f"Invalid port: {self.PORT}. Must be between 1 and 65535")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.LOG_LEVEL not in valid_log_levels:
            errors.append(f"Invalid log level: {self.LOG_LEVEL}. Must be one of {valid_log_levels}")
        
        # Validate workers
        if self.MAX_WORKERS < 1:
            errors.append(f"Invalid max workers: {self.MAX_WORKERS}. Must be at least 1")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary (excluding sensitive data)."""
        sensitive_keys = {"API_KEY", "DATABASE_URL", "REDIS_URL"}
        
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith("_") and key not in sensitive_keys
        }
    
    def __repr__(self) -> str:
        """String representation of settings."""
        return f"Settings(server={self.SERVER_NAME}, host={self.HOST}:{self.PORT}, env={self.ENVIRONMENT})"


# Global settings instance
settings = Settings()

# Validate settings on import
try:
    settings.validate()
except ValueError as e:
    print(f"⚠️  Configuration Warning: {e}")
    if settings.is_production:
        raise


def configure_logging() -> None:
    """Configure application logging based on settings."""
    if not settings.ENABLE_LOGGING:
        return
    
    # Configure logging format
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Configure handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # File handler (if specified)
    if settings.LOG_FILE:
        log_path = Path(settings.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=settings.log_level_int,
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    # Set specific logger levels if needed
    if settings.DEBUG:
        logging.getLogger("fastmcp").setLevel(logging.DEBUG)
        logging.getLogger("uvicorn").setLevel(logging.DEBUG)
    else:
        logging.getLogger("fastmcp").setLevel(logging.INFO)
        logging.getLogger("uvicorn").setLevel(logging.WARNING)


# Configure logging on import
configure_logging() 