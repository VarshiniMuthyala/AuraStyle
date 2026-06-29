"""
AuraStyle - Search Routes

POST /search/text        → text-only semantic search
POST /search/image       → image-only semantic search
POST /search/multimodal  → text + image combined search
POST /voice-search       → voice transcript search (same as text)
"""

from flask import Blueprint, jsonify, request
from ai_service import get_text_embedding, get_image_embedding, rank_products, cosine_similarity
from database.models import get_products_with_embeddings
from config import config
import numpy as np

search_bp = Blueprint("search", __name__)


def _blend_embeddings(text_emb, image_emb, text_weight=0.5):
    """Blend text and image embeddings with given weight for text."""
    t = np.array(text_emb, dtype=np.float32)
    i = np.array(image_emb, dtype=np.float32)
    blended = text_weight * t + (1 - text_weight) * i
    norm = np.linalg.norm(blended)
    if norm > 0:
        blended = blended / norm
    return blended.tolist()


@search_bp.route("/search/text", methods=["POST"])
def search_text():
    """Semantic text search using CLIP text encoder."""
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"success": False, "error": "Query text is required"}), 400

    try:
        embedding = get_text_embedding(query)
        products = get_products_with_embeddings()
        results = rank_products(embedding, products, top_k=config.TOP_K_RESULTS)
        return jsonify({
            "success": True,
            "query": query,
            "count": len(results),
            "results": results
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@search_bp.route("/search/image", methods=["POST"])
def search_image():
    """Semantic image search using CLIP image encoder."""
    if "image" not in request.files:
        return jsonify({"success": False, "error": "Image file is required"}), 400

    file = request.files["image"]
    image_bytes = file.read()

    try:
        embedding = get_image_embedding(image_bytes)
        products = get_products_with_embeddings()
        results = rank_products(embedding, products, top_k=config.TOP_K_RESULTS)
        return jsonify({
            "success": True,
            "count": len(results),
            "results": results
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@search_bp.route("/search/multimodal", methods=["POST"])
def search_multimodal():
    """Combined text + image search (blended CLIP embeddings)."""
    query = request.form.get("query", "").strip()
    image_file = request.files.get("image")

    if not query and image_file is None:
        return jsonify({"success": False, "error": "Provide text, image, or both"}), 400

    try:
        products = get_products_with_embeddings()

        if query and image_file:
            # Blend embeddings
            text_emb = get_text_embedding(query)
            image_emb = get_image_embedding(image_file.read())
            embedding = _blend_embeddings(text_emb, image_emb, text_weight=0.4)
        elif query:
            embedding = get_text_embedding(query)
        else:
            embedding = get_image_embedding(image_file.read())

        results = rank_products(embedding, products, top_k=config.TOP_K_RESULTS)
        return jsonify({
            "success": True,
            "query": query or "(image only)",
            "count": len(results),
            "results": results
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@search_bp.route("/voice-search", methods=["POST"])
def voice_search():
    """Voice transcript search — treated identically to text search."""
    data = request.get_json(silent=True) or {}
    transcript = data.get("transcript", "").strip()

    if not transcript:
        return jsonify({"success": False, "error": "Voice transcript is required"}), 400

    try:
        embedding = get_text_embedding(transcript)
        products = get_products_with_embeddings()
        results = rank_products(embedding, products, top_k=config.TOP_K_RESULTS)
        return jsonify({
            "success": True,
            "query": transcript,
            "count": len(results),
            "results": results
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
