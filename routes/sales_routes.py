"""
Sales Routes Module (API Controller).

Why this file exists:
Handles HTTP endpoints for processing retail transactions and querying sales ledgers.
Delegates business logic, price snapshots, discount deductions, and inventory adjustments
to SalesService.
"""

from typing import Tuple, Any
from flask import Blueprint, request, Response
from services.sales_service import SalesService
from utils.validators import validate_sale_payload
from utils.helpers import (
    format_response,
    format_error,
    ResourceNotFoundError,
    InsufficientStockError,
    ValidationError,
)

sales_bp = Blueprint("sales_bp", __name__, url_prefix="/api/sales")


@sales_bp.route("", methods=["POST"])
def record_sale() -> Tuple[Response, int]:
    """
    POST /api/sales
    Records a point-of-sale transaction, calculates discounts, and reduces stock.

    Request JSON format:
    {
        "product_id": 1,
        "quantity": 2,
        "discount": 10.0
    }
    """
    payload = request.get_json(silent=True)
    if not payload:
        return format_error("Missing or invalid JSON request body.", status_code=400)

    try:
        # 1. Validate payload structure
        validate_sale_payload(payload)

        # 2. Delegate transaction orchestration to SalesService
        sale = SalesService.create_sale(
            product_id=int(payload["product_id"]),
            quantity=int(payload["quantity"]),
            discount=float(payload.get("discount", 0.0)),
        )

        # 3. Return HTTP 201 Created with transaction details
        return format_response(
            success=True,
            data=sale.to_dict(),
            message="Sale recorded successfully and inventory decremented.",
            status_code=201,
        )

    except InsufficientStockError as err:
        return format_error(str(err), status_code=400)
    except ResourceNotFoundError as err:
        return format_error(str(err), status_code=404)
    except (ValidationError, ValueError) as err:
        return format_error(str(err), status_code=400)
    except Exception as err:
        return format_error(f"Error processing sale: {str(err)}", status_code=500)


@sales_bp.route("", methods=["GET"])
def get_sales_history() -> Tuple[Response, int]:
    """
    GET /api/sales?product_id=1
    Retrieves chronological sales history, optionally filtered by product_id.
    """
    product_id_param = request.args.get("product_id")
    product_id = int(product_id_param) if product_id_param and product_id_param.isdigit() else None

    try:
        sales = SalesService.get_sales_history(product_id=product_id)
        data = [s.to_dict() for s in sales]

        return format_response(
            success=True,
            data=data,
            message=f"Retrieved {len(data)} sales transaction record(s).",
            status_code=200,
        )
    except ResourceNotFoundError as err:
        return format_error(str(err), status_code=404)
    except Exception as err:
        return format_error(f"Error fetching sales history: {str(err)}", status_code=500)
