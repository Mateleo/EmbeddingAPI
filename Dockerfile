# Stage 1: Builder
# Uses a Python image with uv pre-installed for efficient dependency management
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Set working directory
WORKDIR /app

# Copy pyproject.toml and uv.lock first to leverage Docker's build cache
# uv.lock is crucial for reproducible builds. Generate it locally with `uv lock`
COPY pyproject.toml uv.lock ./

# Install project dependencies into a virtual environment
# --locked: Ensures dependencies are installed exactly as specified in uv.lock
# --compile-bytecode: Compiles Python source files to bytecode for faster startup
# --no-install-project: Installs only dependencies, not the project itself yet (improves caching if project changes frequently)
RUN uv sync --locked --compile-bytecode --no-install-project

# Copy the rest of your application code
COPY main.py ./

# Install the project itself (if it were an installable package, but here for completeness)
# uv sync will recognize the existing .venv and ensure it's up-to-date
RUN uv sync --locked --compile-bytecode

# Stage 2: Final image
# Uses a minimal Python slim image to keep the final image size small
FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Copy the created virtual environment from the builder stage
# This includes all installed dependencies and compiled bytecode
COPY --from=builder /app/.venv /app/.venv

# Copy the application code
COPY main.py ./

# Set the PATH to include the virtual environment's bin directory
# This ensures that python and installed packages within .venv are used
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn
# Uvicorn will automatically find the `main:app` module and application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
