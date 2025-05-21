import os
from typing import List, Union

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# --- Configuration ---
MODEL_NAME = "mixedbread-ai/mxbai-embed-large-v1"
# For retrieval, add the prompt for query (not for documents).
# "Represent this sentence for searching relevant passages: "
QUERY_PROMPT = "Represent this sentence for searching relevant passages: "
TRUNCATE_DIMENSIONS = None  # As per example, can be None for full dimensions

# --- Model Loading (Global instance for efficiency) ---
app = FastAPI(
    title="Dead Simple Embedding API (CPU Only)",
    description=f"CPU-only API to get text embeddings using {MODEL_NAME}.",
    version="0.1.0",
)

model: SentenceTransformer = None
device: torch.device = None


@app.on_event("startup")
async def load_model():
    """Load the model onto CPU when the FastAPI application starts."""
    global model, device

    # Force CPU device for a CPU-only build
    device = torch.device("cpu")
    print("Forcing CPU for inference (as per CPU-only build).")

    print(f"Loading SentenceTransformer model: {MODEL_NAME} on device: {device}...")
    try:
        model = SentenceTransformer(
            MODEL_NAME, device=device, truncate_dim=TRUNCATE_DIMENSIONS
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
    if model is not None:
        return {"status": "ok", "model_loaded": True, "device": str(device)}
    return {"status": "loading_model", "model_loaded": False, "device": "unknown"}


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

    texts_to_encode = request.text
    if request.is_query:
        if isinstance(texts_to_encode, str):
            texts_to_encode = QUERY_PROMPT + texts_to_encode
        elif isinstance(texts_to_encode, list):
            texts_to_encode = [QUERY_PROMPT + t for t in texts_to_encode]

    try:
        # Encode the text(s).
        # model.encode automatically handles single string vs. list of strings
        # It returns a numpy array, convert to list for JSON serialization
        embeddings = model.encode(texts_to_encode).tolist()
        return EmbedResponse(embeddings=embeddings)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error during embedding generation: {e}"
        )


# Example usage (same as before):
# For a document:
# curl -X POST "http://localhost:8000/embed" -H "Content-Type: application/json" -d '{"text": "A man is eating a piece of bread"}'
# For a query:
# curl -X POST "http://localhost:8000/embed" -H "Content-Type: application/json" -d '{"text": "What is he eating?", "is_query": true}'
# For multiple texts (documents):
# curl -X POST "http://localhost:8000/embed" -H "Content-Type: application/json" -d '{"text": ["A man is eating a piece of bread", "The girl is carrying a baby"]}'
