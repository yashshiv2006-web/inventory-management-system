"""
Inventory Routes Module (API Controller).

Why this file exists:
Handles HTTP requests relating to stock inspection, replenishments (stock additions),
manual stock deductions, and low-stock alert monitoring.
All actual inventory mathematics and threshold verifications are delegated to InventoryService.
"""

from typing import Tuple, Any
from flask import Blueprint, request, Response
from services.inventory_service import InventoryService
from utils.validators import validate_inventory_adjustment
from utils.helpers import (
    format_response,
    format_error,
    ResourceNotFoundError,
    InsufficientStockError,
    ValidationError,
)

inventory_bp = Blueprint("inventory_bp", __name__, url_prefix="/api/inventory")


@inventory_bp.route("/<int:product_id>", methods=["GET"])
def check_stock(product_id: int) -> Tuple[Response, int]:
    """
    GET /api/inventory/<product_id>
    Returns current stock level, threshold alert status, and replenishment timestamp.
    """
    try:
        stock_info = InventoryService.check_stock(product_id)
        return format_response(
            success=True,
            data=stock_info,
            message="Inventory status retrieved successfully.",
            status_code=200,
        )
    except ResourceNotFoundError as err:
        return format_error(str(err), status_code=404)
    except Exception as err:
        return format_error(f"Error checking stock: {str(err)}", status_code=500)


@inventory_bp.route("/<int:product_id>/increase", methods=["POST"])
def increase_stock(product_id: int) -> Tuple[Response, int]:
    """
    POST /api/inventory/<product_id>/increase
    Restocks a product by adding the specified quantity.

    Request JSON format:
    {
        "quantity": 25
    }
    """
    payload = request.get_json(silent=True)
    if not payload or "quantity" not in payload:
        return format_error("Field 'quantity' is required in JSON body.", status_code=400)

    try:
        validated_qty = validate_inventory_adjustment(payload["quantity"])
        updated_inv = InventoryService.increase_stock(product_id, validated_qty)

        return format_response(
            success=True,
            data=updated_inv.to_dict(),
            message=f"Stock successfully increased by {validated_qty} units.",
            status_code=200,
        )
    except (ValidationError, ValueError) as err:
        return format_error(str(err), status_code=400)
    except ResourceNotFoundError as err:
        return format_error(str(err), status_code=404)
    except Exception as err:
        return format_error(f"Error restocking: {str(err)}", status_code=500)


@inventory_bp.route("/<int:product_id>/decrease", methods=["POST"])
def decrease_stock(product_id: int) -> Tuple[Response, int]:
    """
    POST /api/inventory/<product_id>/decrease
    Manually deducts stock units (e.g. damaged goods, store write-offs).

    Request JSON format:
    {
        "quantity": 5
    }
    """
    payload = request.get_json(silent=True)
    if not payload or "quantity" not in payload:
        return format_error("Field 'quantity' is required in JSON body.", status_code=400)

    try:
        validated_qty = validate_inventory_adjustment(payload["quantity"])
        updated_inv = InventoryService.decrease_stock(product_id, validated_qty)

        return format_response(
            success=True,
            data=updated_inv.to_dict(),
            message=f"Stock successfully decreased by {validated_qty} units.",
            status_code=200,
        )
    except InsufficientStockError as err:
        return format_error(str(err), status_code=400)
    except (ValidationError, ValueError) as err:
        return format_error(str(err), status_code=400)
    except ResourceNotFoundError as err:
        return format_error(str(err), status_code=404)
    except Exception as err:
        return format_error(f"Error decreasing stock: {str(err)}", status_code=500)


@inventory_bp.route("/low-stock", methods=["GET"])
def get_low_stock() -> Tuple[Response, int]:
    """
    GET /api/inventory/low-stock?threshold=15
    Lists all products whose stock is at or below their alert threshold.
    """
    threshold_param = request.args.get("threshold")
    threshold = int(threshold_param) if threshold_param and threshold_param.isdigit() else None

    try:
        low_stock_items = InventoryService.get_low_stock_products(threshold=threshold)
        return format_response(
            success=True,
            data=low_stock_items,
            message=f"Identified {len(low_stock_items)} low-stock product(s) needing reorder.",
            status_code=200,
        )
    except Exception as err:
        return format_error(f"Error fetching low stock items: {str(err)}", status_code=500)
