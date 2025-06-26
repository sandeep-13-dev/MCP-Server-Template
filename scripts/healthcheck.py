#!/usr/bin/env python3
"""
Health check script for MCP Server Template.

This script is used by Docker to monitor the health of the MCP server.
It performs basic connectivity and functionality checks.
"""

import asyncio
import sys
import time
from typing import Dict, Any

try:
    from fastmcp import Client
    import httpx
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class HealthChecker:
    """Health checker for MCP server."""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        """
        Initialize health checker.
        
        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self.mcp_url = f"http://{host}:{port}/mcp"
        self.timeout = 5.0
    
    async def check_http_connectivity(self) -> Dict[str, Any]:
        """
        Check basic HTTP connectivity to the server.
        
        Returns:
            Dict with check results
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.mcp_url)
                
                # For MCP servers, we expect a 405 (Method Not Allowed) for GET requests
                # This indicates the server is running and responding
                if response.status_code in [200, 405]:
                    return {
                        "status": "healthy",
                        "message": "HTTP connectivity OK",
                        "status_code": response.status_code
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": f"Unexpected status code: {response.status_code}",
                        "status_code": response.status_code
                    }
                    
        except httpx.TimeoutException:
            return {
                "status": "unhealthy",
                "message": "Connection timeout",
                "error": "timeout"
            }
        except httpx.ConnectError:
            return {
                "status": "unhealthy", 
                "message": "Connection refused",
                "error": "connection_refused"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"HTTP check failed: {str(e)}",
                "error": "unknown"
            }
    
    async def check_mcp_functionality(self) -> Dict[str, Any]:
        """
        Check MCP server functionality by attempting to connect and list tools.
        
        Returns:
            Dict with check results
        """
        try:
            client = Client(self.mcp_url)
            
            async with client:
                # Try to ping the server
                await asyncio.wait_for(client.ping(), timeout=self.timeout)
                
                # Try to list tools
                tools = await asyncio.wait_for(client.list_tools(), timeout=self.timeout)
                
                return {
                    "status": "healthy",
                    "message": "MCP functionality OK",
                    "tools_count": len(tools)
                }
                
        except asyncio.TimeoutError:
            return {
                "status": "unhealthy",
                "message": "MCP functionality check timeout",
                "error": "timeout"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"MCP functionality check failed: {str(e)}",
                "error": "mcp_error"
            }
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """
        Check basic system resources.
        
        Returns:
            Dict with check results
        """
        try:
            import psutil
            
            # Check memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Determine status based on resource usage
            if memory_percent > 95 or cpu_percent > 95:
                status = "unhealthy"
                message = f"High resource usage: Memory {memory_percent}%, CPU {cpu_percent}%"
            elif memory_percent > 80 or cpu_percent > 80:
                status = "warning"
                message = f"Moderate resource usage: Memory {memory_percent}%, CPU {cpu_percent}%"
            else:
                status = "healthy"
                message = "System resources OK"
            
            return {
                "status": status,
                "message": message,
                "memory_percent": memory_percent,
                "cpu_percent": cpu_percent
            }
            
        except ImportError:
            return {
                "status": "warning",
                "message": "psutil not available, skipping resource check",
                "error": "psutil_missing"
            }
        except Exception as e:
            return {
                "status": "warning",
                "message": f"Resource check failed: {str(e)}",
                "error": "resource_check_error"
            }
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all health checks.
        
        Returns:
            Dict with overall health status
        """
        start_time = time.time()
        
        checks = {
            "http": await self.check_http_connectivity(),
            "mcp": await self.check_mcp_functionality(),
            "resources": await self.check_system_resources()
        }
        
        # Determine overall status
        statuses = [check["status"] for check in checks.values()]
        
        if any(status == "unhealthy" for status in statuses):
            overall_status = "unhealthy"
        elif any(status == "warning" for status in statuses):
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        execution_time = time.time() - start_time
        
        return {
            "overall_status": overall_status,
            "checks": checks,
            "execution_time": round(execution_time, 3),
            "timestamp": time.time()
        }


async def main():
    """Main health check function."""
    # Read configuration from environment
    import os
    
    host = os.getenv("MCP_HOST", "localhost")
    port = int(os.getenv("MCP_PORT", "8000"))
    
    # Create health checker
    checker = HealthChecker(host, port)
    
    try:
        # Run health checks
        result = await checker.run_all_checks()
        
        # Print results
        overall_status = result["overall_status"]
        execution_time = result["execution_time"]
        
        if overall_status == "healthy":
            print(f"✅ Health check PASSED (took {execution_time}s)")
            
            # Print details if verbose
            if os.getenv("HEALTH_CHECK_VERBOSE", "false").lower() == "true":
                for check_name, check_result in result["checks"].items():
                    print(f"   • {check_name}: {check_result['message']}")
            
            sys.exit(0)
            
        elif overall_status == "warning":
            print(f"⚠️  Health check WARNING (took {execution_time}s)")
            
            for check_name, check_result in result["checks"].items():
                if check_result["status"] in ["warning", "unhealthy"]:
                    print(f"   • {check_name}: {check_result['message']}")
            
            # Exit with 0 for warnings (container still considered healthy)
            sys.exit(0)
            
        else:  # unhealthy
            print(f"❌ Health check FAILED (took {execution_time}s)")
            
            for check_name, check_result in result["checks"].items():
                if check_result["status"] == "unhealthy":
                    print(f"   • {check_name}: {check_result['message']}")
            
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Health check ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 