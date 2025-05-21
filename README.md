# 🧠 Simple Embeddings API: Crisp & Containerized

Leverage the power of `mixedbread-ai/mxbai-embed-large-v1` with a dead simple, modern, and containerized API. Built for
efficiency and ease of deployment, this service provides text embeddings for all your CPU-bound needs.

---

## ✨ Features

- **`mxbai-embed-large-v1` Integration**: Directly uses the highly-rated Mixedbread AI embedding model.
- **FastAPI Foundation**: A robust, modern, and auto-documenting API framework.
- **`uv` & `pyproject.toml`**: Blazing-fast dependency management and modern project configuration for reproducible
  builds.
- **Dockerized (CPU-Only)**: Optimized multi-stage Dockerfile for a minimal, CPU-efficient deployment.
- **Query Prompt Support**: Seamlessly applies the recommended retrieval prompt
  (`Represent this sentence for searching relevant passages: `) for queries.
- **Health Check**: Monitor service status with a simple `/health` endpoint.

## 🚀 Quickstart

Get your embeddings service up and running in minutes!

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/simple-embeddings-api.git
    cd simple-embeddings-api
    ```

2.  **Generate `uv.lock`**: _(Requires `uv` installed locally: `curl -LsSf https://astral.sh/uv/install.sh | sh`)_

    ```bash
    uv lock
    ```

    This pins all your dependencies for reproducible Docker builds.

3.  **Build the Docker Image**:

    ```bash
    docker build -t simple-embedding-api-cpu .
    ```

4.  **Run the Container**:
    ```bash
    docker run -d -p 8000:8000 --name embeddings_service simple-embedding-api-cpu
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

This project embraces cutting-edge Python tooling for a lean and efficient deployment:

- **`pyproject.toml`**: The single source of truth for project metadata and dependencies.
- **`uv`**: Our chosen package manager for lightning-fast installs and strict lockfile management.
- **Multi-Stage Dockerfile**: Builds a tiny final image by separating build-time dependencies from runtime requirements,
  ensuring only what's necessary is shipped.

---

## 📄 License

This project is licensed under the Apache 2.0 License, matching the `mxbai-embed-large-v1` model's license.
