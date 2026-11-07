"""
Product Routes Module (API Controller).

Why this file exists:
In clean architecture, Route Handlers (or Controllers) act as the HTTP interface:
1. They parse incoming HTTP requests (JSON body, query parameters, path variables).
2. They invoke input validation functions.
3. They delegate business operations to the appropriate Service class (ProductService).
4. They catch domain exceptions and map them to HTTP status codes (200, 201, 400, 404, 409).
5. They NEVER run direct SQL queries!
"""

from typing import Tuple, Any
from flask import Blueprint, request, Response
from services.product_service import ProductService
from utils.validators import validate_product_payload
from utils.helpers import (
    format_response,
    format_error,
    ResourceNotFoundError,
    DuplicateResourceError,
    ValidationError,
)

# Create a Flask Blueprint for product endpoints
product_bp = Blueprint("product_bp", __name__, url_prefix="/api/products")


@product_bp.route("", methods=["POST"])
def add_product() -> Tuple[Response, int]:
    """
    POST /api/products
    Registers a new product in the retail catalog and creates its inventory entry.

    Request JSON format:
    {
        "sku": "ELEC-1001",
        "name": "Wireless Ergonomic Mouse",
        "category": "Electronics",
        "price": 29.99,
        "description": "2.4GHz optical mouse",
        "initial_stock": 50,
        "low_stock_threshold": 10
    }
    """
    # 1. Parse JSON body from request
    payload = request.get_json(silent=True)
    if not payload:
        return format_error("Missing or invalid JSON request body.", status_code=400)

    try:
        # 2. Validate input schema
        validate_product_payload(payload)

        # 3. Delegate creation to the ProductService
        product = ProductService.add_product(
            sku=payload["sku"],
            name=payload["name"],
            category=payload["category"],
            price=float(payload["price"]),
            description=payload.get("description", ""),
            initial_stock=int(payload.get("initial_stock", 0)),
            low_stock_threshold=int(payload.get("low_stock_threshold", 10)),
        )

        # 4. Return success response with HTTP 201 Created
        return format_response(
            success=True,
            data=product.to_dict(),
            message="Product registered successfully.",
            status_code=201,
        )

    except (ValidationError, ValueError) as err:
        return format_error(str(err), status_code=400)
    except DuplicateResourceError as err:
        return format_error(str(err), status_code=409)
    except Exception as err:
        return format_error(f"Internal server error: {str(err)}", status_code=500)


@product_bp.route("", methods=["GET"])
def list_products() -> Tuple[Response, int]:
    """
    GET /api/products
    Retrieves a list of all products in the catalog along with current stock levels.
    """
    try:
        products = ProductService.list_products()
        data = [prod.to_dict() for prod in products]
        return format_response(
            success=True,
            data=data,
            message=f"Retrieved {len(data)} product(s).",
            status_code=200,
        )
    except Exception as err:
        return format_error(f"Failed to fetch products: {str(err)}", status_code=500)


@product_bp.route("/search", methods=["GET"])
def search_product() -> Tuple[Response, int]:
    """
    GET /api/products/search?q=mouse
    Searches for products matching a keyword across name, category, and SKU.
    """
    keyword = request.args.get("q", "").strip()

    try:
        matched = ProductService.search_product(keyword)
        data = [prod.to_dict() for prod in matched]
        return format_response(
            success=True,
            data=data,
            message=f"Found {len(data)} product(s) matching '{keyword}'.",
            status_code=200,
        )
    except Exception as err:
        return format_error(f"Search failed: {str(err)}", status_code=500)


@product_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id: int) -> Tuple[Response, int]:
    """
    GET /api/products/<product_id>
    Fetches detailed metadata and real-time inventory for a specific product.
    """
    try:
        product = ProductService.get_product_by_id(product_id)
        return format_response(
            success=True,
            data=product.to_dict(),
            message="Product retrieved successfully.",
            status_code=200,
        )
    except ResourceNotFoundError as err:
        return format_error(str(err), status_code=404)
    except Exception as err:
        return format_error(f"Error fetching product: {str(err)}", status_code=500)


@product_bp.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id: int) -> Tuple[Response, int]:
    """
    PUT /api/products/<product_id>
    Updates editable fields of an existing product.
    """
    payload = request.get_json(silent=True)
    if not payload:
        return format_error("Missing or invalid JSON request body.", status_code=400)

    try:
        updated_product = ProductService.update_product(product_id, **payload)
        return format_response(
            success=True,
            data=updated_product.to_dict(),
            message="Product updated successfully.",
            status_code=200,
        )
    except ResourceNotFoundError as err:
        return format_error(str(err), status_code=404)
    except DuplicateResourceError as err:
        return format_error(str(err), status_code=409)
    except (ValidationError, ValueError) as err:
        return format_error(str(err), status_code=400)
    except Exception as err:
        return format_error(f"Error updating product: {str(err)}", status_code=500)


@product_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: int) -> Tuple[Response, int]:
    """
    DELETE /api/products/<product_id>
    Removes a product and its associated inventory from the store database.
    """
    try:
        ProductService.delete_product(product_id)
        return format_response(
            success=True,
            data=None,
            message=f"Product with ID {product_id} deleted successfully.",
            status_code=200,
        )
    except ResourceNotFoundError as err:
        return format_error(str(err), status_code=404)
    except Exception as err:
        return format_error(f"Error deleting product: {str(err)}", status_code=500)
