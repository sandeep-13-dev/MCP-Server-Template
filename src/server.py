#!/usr/bin/env python3
"""
MCP Server Template - Main Server Implementation

A robust, production-ready FastMCP server with comprehensive features:
- Modular tool/resource/prompt organization
- Lifecycle management
- Configuration management
- Health monitoring
- Error handling
"""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastmcp import FastMCP
from config.settings import settings
from tools import load_tools
from resources import load_resources
from prompts import load_prompts


class MCPServerTemplate:
    """Main MCP Server class with lifecycle management."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.mcp: Optional[FastMCP] = None
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize server resources and components."""
        print(f"🚀 Initializing {settings.SERVER_NAME} v{settings.SERVER_VERSION}")
        
        # Create FastMCP instance
        self.mcp = FastMCP(settings.SERVER_NAME)
        
        # Load all components
        await self._load_components()
        
        # Initialize monitoring and health checks
        if settings.ENABLE_HEALTH_CHECK:
            await self._setup_health_monitoring()
            
        # Initialize metrics collection
        if settings.ENABLE_METRICS:
            await self._setup_metrics()
            
        self.is_initialized = True
        print(f"✅ {settings.SERVER_NAME} initialized successfully")
        
    async def _load_components(self) -> None:
        """Load tools, resources, and prompts."""
        try:
            # Load tools
            tools_count = await load_tools(self.mcp)
            print(f"📊 Loaded {tools_count} tools")
            
            # Load resources
            resources_count = await load_resources(self.mcp)
            print(f"📚 Loaded {resources_count} resources")
            
            # Load prompts
            prompts_count = await load_prompts(self.mcp)
            print(f"💬 Loaded {prompts_count} prompts")
            
        except Exception as e:
            print(f"❌ Error loading components: {e}")
            raise
            
    async def _setup_health_monitoring(self) -> None:
        """Setup health check endpoints and monitoring."""
        print("📊 Setting up health monitoring...")
        
        @self.mcp.tool
        async def health_check() -> Dict[str, Any]:
            """Check server health status."""
            return {
                "status": "healthy",
                "server": settings.SERVER_NAME,
                "version": settings.SERVER_VERSION,
                "timestamp": asyncio.get_event_loop().time(),
                "initialized": self.is_initialized
            }
            
    async def _setup_metrics(self) -> None:
        """Setup metrics collection."""
        print("📈 Setting up metrics collection...")
        # Implement metrics collection logic here
        pass
        
    async def cleanup(self) -> None:
        """Cleanup server resources."""
        print(f"🛑 Shutting down {settings.SERVER_NAME}")
        
        # Cleanup logic here
        # - Close database connections
        # - Stop background tasks
        # - Save state if needed
        
        self.is_initialized = False
        print("✅ Cleanup completed")


# Global server instance
server_instance = MCPServerTemplate()


@asynccontextmanager
async def lifespan(app):
    """Application lifespan manager."""
    # Startup
    await server_instance.initialize()
    
    yield
    
    # Shutdown
    await server_instance.cleanup()


def create_server() -> FastMCP:
    """
    Create and return the configured MCP server.
    
    This function is used for testing and manual server creation.
    """
    if not server_instance.is_initialized:
        # For synchronous contexts, we need to run initialization
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(server_instance.initialize())
        
    return server_instance.mcp


def main():
    """Main entry point for the MCP server."""
    print(f"🌐 Starting {settings.SERVER_NAME} on {settings.HOST}:{settings.PORT}")
    print(f"📡 Transport: {settings.TRANSPORT}")
    print(f"🔗 Endpoint: http://{settings.HOST}:{settings.PORT}/mcp")
    print(f"📋 Description: {settings.SERVER_DESCRIPTION}")
    
    # Initialize server synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server_instance.initialize())
    
    # Run with specified transport
    if settings.TRANSPORT.lower() == "http":
        server_instance.mcp.run(
            transport="http",
            host=settings.HOST,
            port=settings.PORT,
            path="/mcp"
        )
    elif settings.TRANSPORT.lower() == "sse":
        server_instance.mcp.run(
            transport="sse",
            host=settings.HOST,
            port=settings.PORT,
            path="/sse"
        )
    else:  # stdio
        server_instance.mcp.run(transport="stdio")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        raise 