# Build stage
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN pip install --no-cache-dir build

# Copy source files
COPY pyproject.toml README.md ./
COPY src/ src/

# Build wheel
RUN python -m build --wheel

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser

# Copy wheel from builder
COPY --from=builder /build/dist/*.whl /tmp/

# Install the package
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm -rf /tmp/*.whl

# Create data directory with proper permissions
RUN mkdir -p /app/.data && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MCP_LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import other_agents_mcp; print('OK')" || exit 1

# Default command
ENTRYPOINT ["other-agents-mcp"]
