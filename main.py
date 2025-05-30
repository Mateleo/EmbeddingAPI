import os
from typing import List, Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# --- Configuration ---
# Get model path from environment variable, default to the one expected in Docker
# When running locally without Docker, it will still download from HF if not found.
# In Docker, we'll explicitly set MODEL_PATH to the local directory where the model is staged.
MODEL_PATH = os.getenv("MODEL_PATH", "mixedbread-ai/mxbai-embed-large-v1")
# For retrieval, add the prompt for query (not for documents).
QUERY_PROMPT = "Represent this sentence for searching relevant passages: "
TRUNCATE_DIMENSIONS = None  # As per example, can be None for full dimensions

# --- Model Loading (Global instance for efficiency) ---
app = FastAPI(
    title="Simple Embeddings API (CPU Only)",
    description=f"CPU-only API to get text embeddings using {MODEL_PATH}.",
    version="0.1.0",
)

model: SentenceTransformer | None = None
device = None


@app.on_event("startup")
async def load_model():
    """Load the model onto CPU when the FastAPI application starts."""
    global model, device

    # SentenceTransformers will default to CPU if a GPU is not available
    device = "cpu"
    print("Attempting to load model on CPU.")

    print(
        f"Loading SentenceTransformer model from: {MODEL_PATH} on device: {device}..."
    )
    try:
        # Load from local path if MODEL_PATH is a directory, else from HF Hub
        model = SentenceTransformer(
            MODEL_PATH, device=device, truncate_dim=TRUNCATE_DIMENSIONS
        )
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        raise RuntimeError(f"Could not load the embedding model: {e}")


# --- Pydantic Models for Request/Response ---
class EmbedRequest(BaseModel):
    """Request body for embedding text."""

    text: Union[str, List[str]]
    is_query: bool = False  # Set to True if this text is a query for retrieval


class EmbedResponse(BaseModel):
    """Response body containing the embeddings."""

    embeddings: List[List[float]]  # List of lists because model.encode returns 2D array


# --- API Endpoints ---
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    status = {
        "status": "ok" if model is not None else "loading_model",
        "model_loaded": model is not None,
        "device": "cpu" if model is not None else "unknown",
    }
    return status


@app.post("/embed", response_model=EmbedResponse)
async def get_embeddings(request: EmbedRequest):
    """
    Returns embeddings for the given text(s).
    Optionally, specify `is_query=True` to apply the retrieval prompt.
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded yet. Please try again in a moment.",
        )

    if not request.text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    # Ensure texts_to_encode is always a list
    texts_to_encode = request.text
    if isinstance(texts_to_encode, str):
        texts_to_encode = [texts_to_encode]  # Wrap the single string in a list
    elif not isinstance(texts_to_encode, list):
        raise HTTPException(
            status_code=400, detail="Input text must be a string or a list of strings."
        )

    if request.is_query:
        texts_to_encode = [QUERY_PROMPT + t for t in texts_to_encode]
    try:
        # Encode the text(s).
        # SentenceTransformer's encode method handles batched input.
        embeddings = model.encode(texts_to_encode).tolist()
        return EmbedResponse(embeddings=embeddings)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error during embedding generation: {e}"
        )
