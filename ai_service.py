"""
AuraStyle - CLIP AI Service
Handles CLIP model loading and embedding generation for text and images.
"""

import io
import numpy as np
import torch
from PIL import Image

# CLIP is imported lazily so the app can start even without GPU
_clip = None
_model = None
_preprocess = None
_device = None


def _load_clip():
    """Lazy-load the CLIP model on first use."""
    global _clip, _model, _preprocess, _device
    if _model is None:
        import clip  # type: ignore
        _clip = clip
        _device = "cuda" if torch.cuda.is_available() else "cpu"
        _model, _preprocess = clip.load("ViT-B/32", device=_device)
        _model.eval()
    return _model, _preprocess, _device


def get_text_embedding(text: str) -> list:
    """
    Generate a CLIP text embedding for the given string.
    Returns a Python list of floats.
    """
    model, _, device = _load_clip()
    import clip  # type: ignore
    with torch.no_grad():
        tokens = clip.tokenize([text], truncate=True).to(device)
        embedding = model.encode_text(tokens)
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
    return embedding.cpu().numpy()[0].tolist()


def get_image_embedding(image_bytes: bytes) -> list:
    """
    Generate a CLIP image embedding from raw image bytes.
    Returns a Python list of floats.
    """
    model, preprocess, device = _load_clip()
    with torch.no_grad():
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = preprocess(image).unsqueeze(0).to(device)
        embedding = model.encode_image(tensor)
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
    return embedding.cpu().numpy()[0].tolist()


def cosine_similarity(vec_a: list, vec_b: list) -> float:
    """Compute cosine similarity between two embedding vectors."""
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def rank_products(query_embedding: list, products: list, top_k: int = 20) -> list:
    """
    Rank products by cosine similarity to the query embedding.
    Each product must have an 'embedding' field.
    Returns the top_k products sorted by similarity (descending),
    each augmented with a 'similarity_score' field.
    """
    scored = []
    for product in products:
        emb = product.get("embedding")
        if emb is None:
            continue
        score = cosine_similarity(query_embedding, emb)
        # Build a clean copy without the raw embedding
        result = {k: v for k, v in product.items() if k != "embedding"}
        result["_id"] = str(result["_id"])
        result["similarity_score"] = round(score * 100, 2)  # percentage
        scored.append(result)

    scored.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored[:top_k]
