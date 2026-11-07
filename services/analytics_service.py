"""
Analytics and Sales Intelligence Service Module.

Why this file exists:
In modern retail, capturing data is only half the battle; business intelligence (BI)
is what drives profitable decisions. This service aggregates transaction records
and inventory ledgers to answer critical executive questions:
1. What is our total store revenue and average order value?
2. Which products are our best-sellers?
3. What is the total monetary value of unsold inventory currently on shelves?
4. How many products urgently require reordering?
"""

from typing import List, Dict, Any
from sqlalchemy import func, desc
from database.db import db
from models.product import Product
from models.inventory import Inventory
from models.sales import Sale


class AnalyticsService:
    """
    Encapsulates business intelligence, revenue metrics, and inventory aggregation queries.
    """

    @staticmethod
    def calculate_total_revenue() -> Dict[str, Any]:
        """
        Calculates aggregate revenue figures across all sales recorded in the system.

        Returns:
            Dict[str, Any]: Comprehensive financial summary containing:
                - total_revenue (float): Sum of all completed sales.
                - total_transactions (int): Total count of sales receipts.
                - total_units_sold (int): Cumulative count of items sold.
                - average_order_value (float): Mean revenue generated per sale transaction.
        """
        # SQLAlchemy aggregation: SUM(total_amount), COUNT(id), SUM(quantity)
        result = db.session.query(
            func.coalesce(func.sum(Sale.total_amount), 0.0).label("total_revenue"),
            func.count(Sale.id).label("total_transactions"),
            func.coalesce(func.sum(Sale.quantity), 0).label("total_units_sold"),
        ).first()

        total_rev = float(result.total_revenue) if result else 0.0
        total_tx = int(result.total_transactions) if result else 0
        total_units = int(result.total_units_sold) if result else 0

        # Calculate Average Order Value (AOV), safely guarding against division by zero
        avg_order_value = round(total_rev / total_tx, 2) if total_tx > 0 else 0.0

        return {
            "total_revenue": round(total_rev, 2),
            "total_transactions": total_tx,
            "total_units_sold": total_units,
            "average_order_value": avg_order_value,
        }

    @staticmethod
    def get_top_selling_products(limit: int = 5) -> List[Dict[str, Any]]:
        """
        Identifies best-selling products by aggregating historical sales volume and revenue.

        SQL Equivalent:
            SELECT product_id, SUM(quantity) as total_units, SUM(total_amount) as total_sales
            FROM sales
            GROUP BY product_id
            ORDER BY total_units DESC
            LIMIT :limit;

        Args:
            limit (int, optional): Number of top products to return. Defaults to 5.

        Returns:
            List[Dict[str, Any]]: Ranked list of top-selling products.
        """
        clean_limit = max(1, int(limit))

        # Perform GROUP BY and SUM aggregation joining Sales with Products
        query = (
            db.session.query(
                Sale.product_id,
                Product.name.label("product_name"),
                Product.sku.label("product_sku"),
                Product.category.label("category"),
                func.sum(Sale.quantity).label("total_units_sold"),
                func.sum(Sale.total_amount).label("total_revenue_generated"),
            )
            .join(Product, Sale.product_id == Product.id)
            .group_by(Sale.product_id, Product.name, Product.sku, Product.category)
            .order_by(desc("total_units_sold"))
            .limit(clean_limit)
            .all()
        )

        top_products: List[Dict[str, Any]] = []
        for rank, row in enumerate(query, start=1):
            top_products.append({
                "rank": rank,
                "product_id": row.product_id,
                "product_name": row.product_name,
                "product_sku": row.product_sku,
                "category": row.category,
                "units_sold": int(row.total_units_sold),
                "revenue_generated": round(float(row.total_revenue_generated), 2),
            })

        return top_products

    @staticmethod
    def get_inventory_summary() -> Dict[str, Any]:
        """
        Computes a high-level snapshot of overall inventory health and asset valuation.

        Metrics calculated:
        - Total unique products in catalog.
        - Total physical units on shelves/warehouse.
        - Total inventory valuation: sum of (product price * current stock quantity).
        - Count of products needing replenishment (low stock).
        - Count of products completely out of stock.

        Returns:
            Dict[str, Any]: Operational inventory intelligence summary.
        """
        # Count total distinct products
        total_products = Product.query.count()

        # Aggregate total physical units in inventory
        total_units_res = db.session.query(
            func.coalesce(func.sum(Inventory.quantity), 0)
        ).scalar()
        total_inventory_units = int(total_units_res) if total_units_res else 0

        # Calculate Total Inventory Asset Value: SUM(Inventory.quantity * Product.price)
        valuation_res = db.session.query(
            func.coalesce(func.sum(Inventory.quantity * Product.price), 0.0)
        ).join(Product, Inventory.product_id == Product.id).scalar()
        total_asset_value = round(float(valuation_res), 2) if valuation_res else 0.0

        # Count low-stock and out-of-stock items
        low_stock_count = (
            Inventory.query.filter(
                Inventory.quantity <= Inventory.low_stock_threshold,
                Inventory.quantity > 0,
            ).count()
        )
        out_of_stock_count = Inventory.query.filter(Inventory.quantity == 0).count()

        # Calculate catalog availability health rate percentage
        in_stock_count = total_products - (low_stock_count + out_of_stock_count)
        health_percentage = (
            round((in_stock_count / total_products) * 100, 1)
            if total_products > 0
            else 100.0
        )

        return {
            "total_products": total_products,
            "total_inventory_units": total_inventory_units,
            "total_inventory_asset_value": total_asset_value,
            "in_stock_products_count": max(0, in_stock_count),
            "low_stock_alerts_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "inventory_health_percentage": health_percentage,
        }
