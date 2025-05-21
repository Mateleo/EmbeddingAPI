# 🧠 Simple Embeddings API: Bring Your Own Model

A simple, modern, and containerized API for text embeddings using compatible Sentence Transformers models. Built for
efficiency and ease of deployment on CPU.

---

## ✨ Features

- **Sentence Transformers Compatibility**: Use any model compatible with the Sentence Transformers library.
- **FastAPI Foundation**: A robust, modern, and auto-documenting API framework.
- **`uv` & `pyproject.toml`**: Fast dependency management and modern project configuration.
- **Dockerized (CPU-Only)**: Optimized multi-stage Dockerfile for a minimal, CPU-efficient deployment.
- **Query Prompt Support**: Optionally apply a query prompt for retrieval tasks.
- **Health Check**: Monitor service status with a simple `/health` endpoint.

## 🚀 Quickstart

Get your embeddings service up and running in minutes!

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Mateleo/EmbeddingAPI.git
    cd EmbeddingAPI
    ```

2.  **Install dependencies and generate `uv.lock`**: _(Requires `uv` installed locally: `curl -LsSf https://astral.sh/uv/install.sh | sh`)_

    ```bash
    uv lock
    uv sync
    ```

3.  **Download the model and run the server**:

    ```bash
    uv run download_model.py
    uv run main.py
    ```

## 💡 Usage

The API is now available at `http://localhost:8000`. Explore the interactive documentation at
`http://localhost:8000/docs`.

### Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","model_loaded":true,"device":"cpu"}
```

### Get Embeddings

Send a POST request to `/embed` with your text. Set `is_query: true` for retrieval-optimized embeddings.

#### For a Document:

```bash
curl -X POST "http://localhost:8000/embed" \
     -H "Content-Type: application/json" \
     -d '{"text": "A man is eating a piece of bread"}' | json_pp
```

#### For a Query:

```bash
curl -X POST "http://localhost:8000/embed" \
     -H "Content-Type: application/json" \
     -d '{"text": "What is he eating?", "is_query": true}' | json_pp
```

#### For Multiple Texts:

```bash
curl -X POST "http://localhost:8000/embed" \
     -H "Content-Type: application/json" \
     -d '{"text": ["A man is eating food.", "The girl is carrying a baby."]}' | json_pp
```

---

## 📦 Under the Hood

This project uses modern Python tooling for a lean and efficient deployment:

- **`pyproject.toml`**: Single source of truth for project metadata and dependencies.
- **`uv`**: Fast package manager for lightning-fast installs and lockfile management.
- **Multi-Stage Dockerfile**: Builds a tiny final image by separating build and runtime dependencies.

---

## 📄 License

This project is licensed under the Apache 2.0 License.
