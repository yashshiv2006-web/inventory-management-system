"""
Demand Forecasting Model Training & Accuracy Benchmark Script.

Purpose:
Simulates historical sales data, computes forecast projections, and benchmarks
model accuracy using Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE).

Why this file exists:
Viva examiners frequently ask:
"How do you evaluate your demand forecasting model?"
Running this script demonstrates data science validation principles (evaluating predictions against actual ground truth).

Usage:
    python -m machine_learning.train_model
"""

import math
from machine_learning.demand_forecasting import RetailDemandForecaster


def evaluate_forecasting_model() -> None:
    """Simulates retail test periods and benchmarks accuracy metrics."""
    print("=" * 65)
    print(" Retail Demand Forecasting - Model Evaluation Benchmark")
    print("=" * 65)

    # Simulated ground-truth daily sales for a 30-day training period
    training_daily_sales = [3, 2, 4, 3, 5, 2, 4, 3, 6, 4, 3, 5, 2, 4, 3,
                            5, 4, 3, 6, 2, 4, 3, 5, 4, 2, 5, 3, 4, 6, 3]

    # Ground-truth actual sales in the following 10-day test period
    actual_test_sales = [4, 3, 5, 4, 3, 5, 4, 3, 6, 4]

    # Step 1: Compute historical velocity
    daily_velocity = RetailDemandForecaster.calculate_run_rate(training_daily_sales, days=30)
    print(f"\n[+] Historical Daily Run Rate: {daily_velocity:.2f} units/day")

    # Step 2: Safety stock calculation
    # Calculate sample variance and std dev
    mean_val = sum(training_daily_sales) / len(training_daily_sales)
    variance = sum((x - mean_val) ** 2 for x in training_daily_sales) / (len(training_daily_sales) - 1)
    std_dev = math.sqrt(variance)

    safety_stock = RetailDemandForecaster.calculate_safety_stock(
        daily_sales_std_dev=std_dev,
        supplier_lead_time_days=5,
        service_factor=1.65,
    )
    print(f"[+] Daily Demand Std Dev:      {std_dev:.2f} units")
    print(f"[+] Computed Safety Stock:     {safety_stock} units (95% Service Level)")

    # Step 3: Evaluate projections across 10-day test horizon
    predicted_per_day = daily_velocity
    errors = [abs(actual - predicted_per_day) for actual in actual_test_sales]
    squared_errors = [(actual - predicted_per_day) ** 2 for actual in actual_test_sales]

    mae = sum(errors) / len(errors)
    rmse = math.sqrt(sum(squared_errors) / len(squared_errors))

    print(f"\n[+] Accuracy Benchmarks on 10-Day Holdout Test Horizon:")
    print(f"    - Mean Absolute Error (MAE):     {mae:.2f} units")
    print(f"    - Root Mean Squared Error (RMSE): {rmse:.2f} units")
    print(f"    - Forecast Accuracy Score:        {max(0.0, 100.0 - (mae / mean_val * 100)):.1f}%")

    print("\n" + "=" * 65)
    print(" Model Benchmark Completed Successfully!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    evaluate_forecasting_model()
