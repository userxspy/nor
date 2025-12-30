# ==========================================
# ⚡ FUTURE-PROOF ULTRA-FAST DOCKERFILE (2025+)
# Latest: Python 3.12 | Debian Bookworm | BuildKit 2.0
# ==========================================

# Stage 1: Base with Python 3.12 (Latest Stable - Dec 2024)
FROM python:3.12-slim-bookworm as base

# Future-proof environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONOPTIMIZE=2 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    UV_SYSTEM_PYTHON=1 \
    MALLOC_TRIM_THRESHOLD_=100000 \
    MALLOC_MMAP_THRESHOLD_=100000

# ==========================================
# Stage 2: Dependencies Builder
# ==========================================
FROM base as builder

# Install minimal build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc-dev \
    libffi-dev \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install UV (Ultra-fast pip alternative - 10-100x faster!)
RUN pip install --no-cache-dir uv

# Copy requirements
COPY requirements.txt /tmp/

# Install dependencies with UV (lightning fast!)
RUN uv pip install --system --no-cache \
    --compile-bytecode \
    -r /tmp/requirements.txt || \
    pip install --no-cache-dir --user --compile \
    -r /tmp/requirements.txt

# Pre-compile all Python files
RUN python -m compileall -b /root/.local 2>/dev/null || \
    python -m compileall /root/.local

# ==========================================
# Stage 3: Ultra-Slim Runtime
# ==========================================
FROM python:3.12-slim-bookworm as runtime

# Metadata with proper labels (OCI standard)
LABEL org.opencontainers.image.title="Auto Filter Bot"
LABEL org.opencontainers.image.description="Ultra-Fast Auto Filter Bot - Future-Proof Edition"
LABEL org.opencontainers.image.version="4.0-2025"
LABEL org.opencontainers.image.authors="Your Name"
LABEL org.opencontainers.image.source="https://github.com/yourusername/repo"
LABEL org.opencontainers.image.licenses="MIT"

# Runtime optimizations (Python 3.12 compatible)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONOPTIMIZE=2 \
    MALLOC_TRIM_THRESHOLD_=100000 \
    MALLOC_MMAP_THRESHOLD_=100000 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPYCACHEPREFIX=/tmp/pycache

# Install only critical runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/* /var/cache/apt/*

# Create non-root user with security best practices
RUN groupadd -r -g 1000 botuser && \
    useradd -r -u 1000 -g botuser -m -s /sbin/nologin botuser && \
    mkdir -p /app /tmp/pycache && \
    chown -R botuser:botuser /app /tmp/pycache

WORKDIR /app

# Copy compiled dependencies from builder
COPY --from=builder --chown=botuser:botuser /root/.local /home/botuser/.local

# Copy application files (excluding unnecessary files via .dockerignore)
COPY --chown=botuser:botuser . .

# Add user's local bin to PATH
ENV PATH=/home/botuser/.local/bin:$PATH

# Switch to non-root user (security best practice)
USER botuser

# Pre-warm critical imports (faster first startup)
RUN python -c "import sys; print(f'Python {sys.version}')" && \
    python -c "import hydrogram; import pymongo; import aiohttp; import asyncio" 2>/dev/null || true

# Lightweight health check (socket-based, no HTTP overhead)
HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --retries=2 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('127.0.0.1', 8080)); s.close()" || exit 1

# Expose port (Koyeb auto-detects)
EXPOSE 8080

# Signal handling for graceful shutdown
STOPSIGNAL SIGTERM

# Use exec form for faster startup + Python optimizations
CMD ["python", "-O", "-u", "bot.py"]
