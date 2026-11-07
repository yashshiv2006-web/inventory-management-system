"""
Excel & CSV Tabular Report Generator Module.

Purpose:
Generates commercial spreadsheet exports (CSV format compatible with Microsoft Excel,
Google Sheets, and Apple Numbers) for inventory asset auditing and sales ledgers.

Why this file exists:
Retail executives and external financial auditors require tabular exports.
This module encapsulates serialization logic using Python's built-in `csv` and `io` libraries.
"""

import csv
import io
from typing import List, Dict, Any


class SpreadsheetReportGenerator:
    """Generates standard CSV spreadsheet strings ready for HTTP download streaming."""

    @staticmethod
    def generate_inventory_csv(products_data: List[Dict[str, Any]]) -> str:
        """
        Creates a CSV representation of the current retail inventory ledger.

        Args:
            products_data (List[Dict[str, Any]]): Product records with stock data.

        Returns:
            str: Comma-separated value text.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow([
            "Product ID",
            "SKU Barcode",
            "Product Name",
            "Category",
            "Unit Selling Price ($)",
            "Current Stock (Units)",
            "Low Stock Threshold",
            "Stock Status",
            "Estimated Asset Valuation ($)",
        ])

        # Data rows
        for p in products_data:
            qty = p.get("current_stock", 0)
            price = p.get("price", 0.0)
            val = qty * price
            status = "LOW STOCK" if p.get("is_low_stock") else "IN STOCK"
            if qty == 0:
                status = "OUT OF STOCK"

            writer.writerow([
                p.get("id"),
                p.get("sku"),
                p.get("name"),
                p.get("category"),
                f"{price:.2f}",
                qty,
                p.get("low_stock_threshold", 10),
                status,
                f"{val:.2f}",
            ])

        return output.getvalue()

    @staticmethod
    def generate_sales_csv(sales_data: List[Dict[str, Any]]) -> str:
        """
        Creates a CSV representation of customer sales transactions.

        Args:
            sales_data (List[Dict[str, Any]]): Sales transaction dictionaries.

        Returns:
            str: Comma-separated value text.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Receipt Number",
            "Product SKU",
            "Product Name",
            "Quantity Sold",
            "Unit Price ($)",
            "Discount Applied (%)",
            "Net Revenue ($)",
            "Transaction Timestamp",
        ])

        for s in sales_data:
            writer.writerow([
                f"TX-{s.get('id', 0):04d}",
                s.get("product_sku", "N/A"),
                s.get("product_name", "N/A"),
                s.get("quantity", 0),
                f"{s.get('unit_price', 0.0):.2f}",
                f"{s.get('discount_percentage', 0.0):.1f}%",
                f"{s.get('total_amount', 0.0):.2f}",
                s.get("sale_date", ""),
            ])

        return output.getvalue()
