"""
Reports & CSV Export Routes Module.

Purpose:
Handles dedicated REST endpoints for generating tabular data streams (CSV format)
for external financial audits and spreadsheet analysis.
"""

from typing import Any
from flask import Blueprint, Response, request
from services.product_service import ProductService
from services.sales_service import SalesService
from reports.excel_generator import SpreadsheetReportGenerator

reports_bp = Blueprint("reports_bp", __name__, url_prefix="/api/reports")


@reports_bp.route("/inventory.csv", methods=["GET"])
def export_inventory_csv() -> Response:
    """Exports inventory ledger in CSV format compatible with Microsoft Excel."""
    products = ProductService.list_products()
    data = [p.to_dict() for p in products]
    csv_content = SpreadsheetReportGenerator.generate_inventory_csv(data)

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=inventory_report.csv"},
    )


@reports_bp.route("/sales.csv", methods=["GET"])
def export_sales_csv() -> Response:
    """Exports sales transaction ledger in CSV format."""
    sales = SalesService.get_sales_history()
    data = [s.to_dict() for s in sales]
    csv_content = SpreadsheetReportGenerator.generate_sales_csv(data)

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=sales_report.csv"},
    )
