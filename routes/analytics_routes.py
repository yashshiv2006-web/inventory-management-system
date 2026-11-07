"""
Analytics and Sales Intelligence Routes Module (API Controller).

Why this file exists:
Provides REST endpoints that expose aggregated metrics, executive KPI summaries,
and stock intelligence computed by AnalyticsService.
"""

from typing import Tuple, Any
from flask import Blueprint, request, Response
from services.analytics_service import AnalyticsService
from utils.helpers import format_response, format_error

analytics_bp = Blueprint("analytics_bp", __name__, url_prefix="/api/analytics")


@analytics_bp.route("/revenue", methods=["GET"])
def get_revenue_metrics() -> Tuple[Response, int]:
    """
    GET /api/analytics/revenue
    Returns total cumulative sales revenue, total transactions, total units sold,
    and average order value (AOV).
    """
    try:
        revenue_data = AnalyticsService.calculate_total_revenue()
        return format_response(
            success=True,
            data=revenue_data,
            message="Revenue analytics computed successfully.",
            status_code=200,
        )
    except Exception as err:
        return format_error(f"Error computing revenue metrics: {str(err)}", status_code=500)


@analytics_bp.route("/top-selling", methods=["GET"])
def get_top_selling() -> Tuple[Response, int]:
    """
    GET /api/analytics/top-selling?limit=5
    Returns ranked list of best-selling products by quantity and revenue generated.
    """
    limit_param = request.args.get("limit", "5")
    limit = int(limit_param) if limit_param.isdigit() else 5

    try:
        top_products = AnalyticsService.get_top_selling_products(limit=limit)
        return format_response(
            success=True,
            data=top_products,
            message=f"Top {len(top_products)} selling product(s) retrieved successfully.",
            status_code=200,
        )
    except Exception as err:
        return format_error(f"Error fetching top selling products: {str(err)}", status_code=500)


@analytics_bp.route("/inventory-summary", methods=["GET"])
def get_inventory_summary() -> Tuple[Response, int]:
    """
    GET /api/analytics/inventory-summary
    Returns overall inventory valuation, product counts, stock health rate,
    and low-stock alerts.
    """
    try:
        summary = AnalyticsService.get_inventory_summary()
        return format_response(
            success=True,
            data=summary,
            message="Inventory summary and valuation computed successfully.",
            status_code=200,
        )
    except Exception as err:
        return format_error(f"Error computing inventory summary: {str(err)}", status_code=500)
