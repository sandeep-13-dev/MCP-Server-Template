# =============================================================================
# MCP Server Template - Production Dockerfile
# =============================================================================

# Use Python 3.11 slim image for smaller size and security
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Essential build tools
    gcc \
    g++ \
    # Networking and security
    curl \
    ca-certificates \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 mcp

# =============================================================================
# Development Stage
# =============================================================================
FROM base as development

# Install UV package manager for faster dependency resolution
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies with development extras
RUN uv pip install --system -e ".[dev]"

# Copy source code
COPY --chown=mcp:mcp . .

# Switch to non-root user
USER mcp

# Development command
CMD ["python", "src/server.py"]

# =============================================================================
# Production Build Stage
# =============================================================================
FROM base as builder

# Install UV for faster package installation
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies in a virtual environment
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install production dependencies only
RUN uv pip install --no-dev .

# =============================================================================
# Production Runtime Stage
# =============================================================================
FROM base as production

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy source code with proper ownership
COPY --chown=mcp:mcp src/ ./src/
COPY --chown=mcp:mcp scripts/ ./scripts/
COPY --chown=mcp:mcp pyproject.toml ./

# Create logs directory
RUN mkdir -p logs && chown mcp:mcp logs

# Switch to non-root user
USER mcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python scripts/healthcheck.py || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "src/server.py"]

# =============================================================================
# Testing Stage
# =============================================================================
FROM development as testing

# Install test dependencies
RUN uv pip install --system -e ".[dev]"

# Copy tests
COPY --chown=mcp:mcp tests/ ./tests/

# Run tests by default
CMD ["python", "-m", "pytest", "-v", "tests/"]

# =============================================================================
# Documentation Stage
# =============================================================================
FROM base as docs

# Install UV
RUN pip install uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install documentation dependencies
RUN uv pip install --system mkdocs mkdocs-material mkdocstrings[python]

# Copy documentation source
COPY --chown=mcp:mcp docs/ ./docs/
COPY --chown=mcp:mcp README.md ./
COPY --chown=mcp:mcp src/ ./src/

# Switch to non-root user
USER mcp

# Expose documentation port
EXPOSE 8080

# Serve documentation
CMD ["mkdocs", "serve", "--dev-addr", "0.0.0.0:8080"]

# =============================================================================
# Labels and Metadata
# =============================================================================
FROM production as final

# Add labels for better container management
LABEL maintainer="your.email@example.com" \
      description="MCP Server Template - Production ready FastMCP server" \
      version="1.0.0" \
      org.opencontainers.image.title="MCP Server Template" \
      org.opencontainers.image.description="A robust template for building FastMCP servers" \
      org.opencontainers.image.vendor="Your Organization" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.schema-version="1.0" \
      org.opencontainers.image.source="https://github.com/your-username/mcp-server-template" \
      org.opencontainers.image.documentation="https://your-username.github.io/mcp-server-template" 