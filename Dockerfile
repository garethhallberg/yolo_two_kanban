# Multi-stage Docker build for Kanban application
# Stage 1: Python dependencies and backend build
FROM python:3.11-slim as python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set PATH to include uv (installed to ~/.local/bin by default)
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy backend requirements
COPY backend/pyproject.toml backend/uv.lock ./

# Install Python dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Copy backend source code
COPY backend/src ./src
COPY backend/tests ./tests
COPY backend/static ./static

# Stage 2: Node.js dependencies and frontend build
FROM node:20-alpine as node-base

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install Node.js dependencies
RUN npm ci --only=production

# Copy frontend source code
COPY frontend ./

# Build NextJS application
RUN npm run build

# Stage 3: Production image
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from python-base stage
COPY --from=python-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-base /usr/local/bin /usr/local/bin

# Copy backend source code
COPY --from=python-base --chown=appuser:appuser /app/src ./src

# Copy frontend build from node-base stage
COPY --from=node-base --chown=appuser:appuser /app/frontend/.next/standalone ./
COPY --from=node-base --chown=appuser:appuser /app/frontend/.next/static ./.next/static
COPY --from=node-base --chown=appuser:appuser /app/frontend/public ./public

# Create static directory for FastAPI to serve
RUN mkdir -p static
COPY --from=node-base --chown=appuser:appuser /app/frontend/out ./static

# Create database directory
RUN mkdir -p data && chmod 755 data

# Copy entrypoint script
COPY --chown=appuser:appuser docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Copy environment file template
COPY .env.example ./.env

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    DATABASE_URL=sqlite:///./data/kanban.db

# Entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]

# Default command
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]