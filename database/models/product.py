"""
AuraStyle - Product Model
Defines the schema and helper functions for the products collection.
"""

from bson import ObjectId
from database.connection import get_collection


def serialize_product(product: dict) -> dict:
    """Convert a MongoDB document to a JSON-serialisable dict."""
    if product is None:
        return None
    product["_id"] = str(product["_id"])
    # Remove embedding from API responses to reduce payload size
    product.pop("embedding", None)
    return product


def get_all_products(limit: int = 100) -> list:
    col = get_collection("products")
    products = list(col.find({}, {"embedding": 0}).limit(limit))
    return [serialize_product(p) for p in products]


def get_product_by_id(product_id: str) -> dict:
    col = get_collection("products")
    try:
        product = col.find_one({"_id": ObjectId(product_id)})
    except Exception:
        return None
    return serialize_product(product)


def get_products_with_embeddings() -> list:
    """Return all products including their CLIP embeddings (for search)."""
    col = get_collection("products")
    return list(col.find({}))
