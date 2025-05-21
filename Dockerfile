# Stage 1: Builder - for installing Python packages and downloading/staging the model
# Using a uv-enabled Python slim image for efficient dependency management
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Set build-time environment variables for uv and model cache
# UV_COMPILE_BYTECODE=1 ensures all uv commands compile bytecode for faster startup
ENV UV_COMPILE_BYTECODE=1
# Temporarily set HF_HOME to a cache directory within /tmp.
# This ensures that default model downloads don't pollute /root/.cache, which is harder to control.
ENV HF_HOME=/tmp/hf_cache

# Copy pyproject.toml and uv.lock to leverage Docker's build cache
# uv.lock is crucial for reproducible builds. Generate it locally with `uv lock`.
COPY pyproject.toml uv.lock ./

# Install Python dependencies (FastAPI, uvicorn, sentence-transformers, torch) into .venv
# --no-install-project ensures only the declared dependencies are installed, not the project itself yet.
RUN uv sync --locked --no-install-project --no-cache && \
    uv pip install --no-cache-dir \
    # Specify the CPU-only version of torch using the index URL
    torch --index-url https://download.pytorch.org/whl/cpu \
    # Install other dependencies from the default index
    sentence-transformers hf-xet 'fastapi[standard]'

# --- FIX: Set PATH to include the virtual environment's bin directory ---
# This ensures that subsequent `python` commands use the interpreter from `.venv`
ENV PATH="/app/.venv/bin:$PATH"

# --- Model Download and Staging ---
# Now, sentence_transformers will be available because Python will find it in /app/.venv/bin
RUN python -c "from sentence_transformers import SentenceTransformer; \
               model = SentenceTransformer('mixedbread-ai/mxbai-embed-large-v1'); \
               model.save_pretrained('/app/model_data')"

# Stage 2: Final - a minimal image for production
# Using a very minimal Python slim image to keep the final image size as small as possible.
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy the virtual environment from the builder stage
# This .venv contains only Python packages (FastAPI, PyTorch, sentence-transformers code), not the large model files.
COPY --from=builder /app/.venv /app/.venv

# Copy the pre-downloaded and staged model files from the builder stage
COPY --from=builder /app/model_data /app/model_data

# Copy the main application file
COPY main.py ./

# Set the PATH environment variable to include the virtual environment's bin directory
# This ensures that python and installed packages within .venv are used
ENV PATH="/app/.venv/bin:$PATH"

# Set a runtime environment variable for the model path that our main.py will use.
# This tells our application where to load the model from within the container.
ENV MODEL_PATH="/app/model_data"

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn
# Uvicorn will automatically find the `main:app` module and application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
