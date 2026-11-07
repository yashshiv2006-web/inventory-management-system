"""
Notification and Alert Dispatcher Module.

Purpose:
Handles real-time threshold notifications, reorder advisories, and system alerts
for retail store managers.

Why this file exists:
In autonomous retail systems, when inventory counts drop to or below safety thresholds,
the platform triggers alert events. This utility provides structured notification logs
and simulated email/SMS dispatches without requiring external third-party paid APIs.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone


class NotificationService:
    """
    Manages generation and logging of inventory stockout warnings and reorder alerts.
    """

    # In-memory alert log buffer for viva demonstration
    _alert_history: List[Dict[str, Any]] = []

    @classmethod
    def send_low_stock_alert(
        cls,
        product_name: str,
        product_sku: str,
        current_stock: int,
        threshold: int,
    ) -> Dict[str, Any]:
        """
        Creates and logs an urgent low-stock warning notice.

        Args:
            product_name (str): Name of the depleted item.
            product_sku (str): Unique barcode identifier.
            current_stock (int): Units remaining on shelf.
            threshold (int): Minimum acceptable safety threshold.

        Returns:
            Dict[str, Any]: Structured notification payload.
        """
        urgency = "CRITICAL" if current_stock == 0 else "WARNING"
        alert_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": urgency,
            "product_name": product_name,
            "sku": product_sku,
            "current_stock": current_stock,
            "threshold": threshold,
            "message": (
                f"[{urgency}] Product '{product_name}' (SKU: {product_sku}) "
                f"has only {current_stock} unit(s) remaining (Threshold: {threshold}). "
                f"Please issue a Purchase Order immediately."
            ),
        }
        cls._alert_history.append(alert_payload)
        return alert_payload

    @classmethod
    def get_recent_alerts(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns the most recent alert logs."""
        return cls._alert_history[-limit:]
