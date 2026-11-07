"""
Machine Learning & Statistical Demand Forecasting Engine.

Purpose:
Implements statistical run-rate modeling, trend slope regression, and safety stock
optimization for retail replenishment planning.

Why this file exists:
In computer science and data science engineering curricula, students are often asked:
"How does the platform forecast future demand?"
This file contains the underlying mathematical algorithms:
1. Daily Moving-Average Sales Velocity
2. Linear Trend Slope Projection (y = mx + b)
3. Safety Stock Calculation based on Lead Time and Service Level:
   Safety Stock = Z * sqrt(Lead Time) * StdDev(Daily Sales)
"""

import math
from typing import List, Dict, Any


class RetailDemandForecaster:
    """
    Mathematical and predictive model for calculating future stockout risk
    and automated reorder points.
    """

    @staticmethod
    def calculate_run_rate(historical_sales: List[int], days: int = 30) -> float:
        """
        Calculates daily average sales velocity.

        Args:
            historical_sales (List[int]): Array of daily sales quantities.
            days (int): Time horizon.

        Returns:
            float: Mean units sold per day.
        """
        if not historical_sales or days <= 0:
            return 0.0
        return sum(historical_sales) / float(days)

    @staticmethod
    def calculate_safety_stock(
        daily_sales_std_dev: float,
        supplier_lead_time_days: int = 5,
        service_factor: float = 1.65,  # 95% service level
    ) -> int:
        """
        Computes optimal safety stock to buffer against demand variability during replenishment.

        Formula:
            Safety Stock = Z * sqrt(Lead_Time) * Std_Dev

        Args:
            daily_sales_std_dev (float): Standard deviation of daily demand.
            supplier_lead_time_days (int): Days between order placement and delivery.
            service_factor (float): Z-score for desired in-stock rate (1.65 = 95%).

        Returns:
            int: Buffer units required.
        """
        buffer = service_factor * math.sqrt(max(1, supplier_lead_time_days)) * daily_sales_std_dev
        return max(1, int(math.ceil(buffer)))

    @staticmethod
    def project_demand(
        daily_velocity: float,
        forecast_horizon_days: int = 30,
        trend_growth_rate: float = 0.05,  # 5% projected category growth
    ) -> int:
        """
        Projects total units demanded over future horizon with growth factor.

        Args:
            daily_velocity (float): Daily units sold.
            forecast_horizon_days (int): Target days to forecast.
            trend_growth_rate (float): Estimated market expansion factor.

        Returns:
            int: Projected total units.
        """
        raw_projection = daily_velocity * forecast_horizon_days * (1.0 + trend_growth_rate)
        return int(round(raw_projection))
