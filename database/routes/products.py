"""
AuraStyle - Products Routes
GET /products        → all products (no embeddings)
GET /product/<id>    → single product by MongoDB ObjectId
"""

from flask import Blueprint, jsonify, request
from database.models import get_all_products, get_product_by_id

products_bp = Blueprint("products", __name__)


@products_bp.route("/products", methods=["GET"])
def list_products():
    """Return all products. Supports optional ?category= and ?gender= filters."""
    products = get_all_products(limit=200)

    # Optional query-param filters
    category = request.args.get("category", "").strip().lower()
    gender = request.args.get("gender", "").strip().lower()

    if category:
        products = [p for p in products if p.get("category", "").lower() == category]
    if gender:
        products = [p for p in products if p.get("gender", "").lower() == gender]

    return jsonify({"success": True, "count": len(products), "products": products})


@products_bp.route("/product/<product_id>", methods=["GET"])
def get_product(product_id: str):
    """Return a single product by its MongoDB _id."""
    product = get_product_by_id(product_id)
    if product is None:
        return jsonify({"success": False, "error": "Product not found"}), 404
    return jsonify({"success": True, "product": product})
