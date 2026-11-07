"""
Demand Forecasting and Stock Optimization Service Module.

Why this file exists:
Retail stock optimization prevents two expensive mistakes:
1. Stockouts (Lost revenue from empty shelves)
2. Overstocking (Tied-up cash flow and storage costs)

This service computes predictive sales demand using historical sales velocity,
moving averages, and safety stock calculations.
Formula used:
- Daily Run Rate = (Total Historical Sales Units / Active Window Days)
- Forecasted 30-Day Demand = Daily Run Rate * 30 * Seasonal Growth Factor
- Recommended Reorder Quantity = Max(0, (Forecasted Demand + Safety Stock) - Current Stock)
"""

from typing import List, Dict, Any
from sqlalchemy import func
from database.db import db
from models.product import Product
from models.inventory import Inventory
from models.sales import Sale


class ForecastingService:
    """
    Provides predictive retail intelligence, run-rate calculations,
    and automatic reorder quantity recommendations.
    """

    @staticmethod
    def predict_demand(forecast_days: int = 30) -> List[Dict[str, Any]]:
        """
        Computes projected sales demand and replenishment needs for every catalog product.

        Args:
            forecast_days (int): Horizon period in days (default: 30 days).

        Returns:
            List[Dict[str, Any]]: List of forecasting summaries per product.
        """
        products = Product.query.order_by(Product.name.asc()).all()
        forecasts: List[Dict[str, Any]] = []

        for prod in products:
            # Aggregate total units sold historically for this product
            total_sold_res = db.session.query(
                func.coalesce(func.sum(Sale.quantity), 0)
            ).filter(Sale.product_id == prod.id).scalar()
            total_units_sold = int(total_sold_res) if total_sold_res else 0

            # Current stock level
            current_stock = prod.inventory.quantity if prod.inventory else 0
            threshold = prod.inventory.low_stock_threshold if prod.inventory else 10

            # Estimate velocity (assuming sample historical period of 30 days minimum)
            # Daily sales velocity (run-rate)
            daily_velocity = max(0.1, total_units_sold / 30.0)

            # Projected demand over the requested window
            projected_demand = int(round(daily_velocity * forecast_days))

            # Safety Stock: buffer inventory to handle demand spikes (typically 1.5x threshold)
            safety_stock = int(round(threshold * 1.5))

            # Recommended Reorder = (Forecasted Demand + Safety Stock) - Current Stock
            recommended_reorder = max(0, (projected_demand + safety_stock) - current_stock)

            # Stockout risk assessment
            if current_stock == 0:
                risk_level = "CRITICAL (Stockout)"
                risk_badge = "danger"
            elif current_stock < projected_demand:
                risk_level = "HIGH (Reorder Needed)"
                risk_badge = "warning"
            elif current_stock < (projected_demand + safety_stock):
                risk_level = "MODERATE"
                risk_badge = "info"
            else:
                risk_level = "OPTIMAL (Healthy Stock)"
                risk_badge = "success"

            forecasts.append({
                "product_id": prod.id,
                "product_name": prod.name,
                "product_sku": prod.sku,
                "category": prod.category,
                "current_stock": current_stock,
                "historical_units_sold": total_units_sold,
                "daily_run_rate": round(daily_velocity, 2),
                "projected_demand_30d": projected_demand,
                "safety_stock": safety_stock,
                "recommended_reorder": recommended_reorder,
                "risk_level": risk_level,
                "risk_badge": risk_badge,
            })

        return forecasts

    @staticmethod
    def get_summary_metrics() -> Dict[str, Any]:
        """Provides high-level demand forecast statistics for dashboard cards."""
        forecasts = ForecastingService.predict_demand(forecast_days=30)
        total_predicted_demand = sum(f["projected_demand_30d"] for f in forecasts)
        items_needing_reorder = sum(1 for f in forecasts if f["recommended_reorder"] > 0)
        total_recommended_units = sum(f["recommended_reorder"] for f in forecasts)

        return {
            "total_predicted_demand_units": total_predicted_demand,
            "products_at_risk_count": items_needing_reorder,
            "total_recommended_reorder_units": total_recommended_units,
        }
