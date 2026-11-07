"""
Inventory Model Module.

This file defines the Inventory entity using SQLAlchemy ORM.
In retail architecture, keeping the product catalog separate from the inventory ledger
is a standard best practice because:
1. Product metadata (title, category, price) rarely changes.
2. Inventory levels (quantity on hand, restock timestamps) change continuously with every sale and shipment.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from database.db import db


class Inventory(db.Model):
    """
    Represents the real-time stock levels and threshold alerts for a product.

    Attributes:
        id (int): Primary key.
        product_id (int): Foreign key referencing the parent Product.
        quantity (int): Number of units currently available on the retail shelf/warehouse.
        low_stock_threshold (int): Minimum acceptable count before flagging a reorder alert.
        last_restocked_at (datetime): Timestamp when stock was last increased.
        updated_at (datetime): Timestamp of the most recent stock modification.
    """

    __tablename__ = "inventory"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Key pointing to the Product's ID.
    # `unique=True` enforces the 1-to-1 relationship: one product has exactly one inventory entry.
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Quantity of physical items in stock. Defaults to 0 upon creation.
    quantity = db.Column(db.Integer, default=0, nullable=False)

    # Minimum stock count before the system generates a 'Low Stock' alert for store managers.
    low_stock_threshold = db.Column(db.Integer, default=10, nullable=False)

    # Keeps track of the last time new stock was received/replenished.
    last_restocked_at = db.Column(db.DateTime, nullable=True)

    # Automatically records when this inventory record was last updated.
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Bi-directional relationship back to the Product entity
    product = db.relationship("Product", back_populates="inventory")

    def __init__(
        self,
        product_id: int,
        quantity: int = 0,
        low_stock_threshold: int = 10,
        last_restocked_at: Optional[datetime] = None,
    ) -> None:
        """
        Constructor to initialize a new Inventory record.

        Args:
            product_id (int): ID of the product this inventory belongs to.
            quantity (int, optional): Initial stock level. Defaults to 0.
            low_stock_threshold (int, optional): Warning threshold. Defaults to 10.
            last_restocked_at (datetime, optional): Time of initial stocking.
        """
        self.product_id = product_id
        self.quantity = max(0, int(quantity))
        self.low_stock_threshold = max(0, int(low_stock_threshold))
        self.last_restocked_at = last_restocked_at or datetime.now(timezone.utc)

    def is_low_stock(self) -> bool:
        """
        Business Rule: Evaluates whether the current stock level is at or below
        the configured low stock threshold.

        Returns:
            bool: True if quantity <= low_stock_threshold, False otherwise.
        """
        return self.quantity <= self.low_stock_threshold

    def get_stock_status(self) -> str:
        """
        Returns a human-readable inventory health status string.
        Helpful for retail managers and dashboard summaries.

        Returns:
            str: "OUT_OF_STOCK", "LOW_STOCK", or "IN_STOCK"
        """
        if self.quantity <= 0:
            return "OUT_OF_STOCK"
        elif self.quantity <= self.low_stock_threshold:
            return "LOW_STOCK"
        return "IN_STOCK"

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the inventory record into a Python dictionary.

        Returns:
            Dict[str, Any]: Dictionary containing stock levels, status, and product details.
        """
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "product_sku": self.product.sku if self.product else None,
            "quantity": self.quantity,
            "low_stock_threshold": self.low_stock_threshold,
            "status": self.get_stock_status(),
            "is_low_stock": self.is_low_stock(),
            "last_restocked_at": (
                self.last_restocked_at.isoformat() if self.last_restocked_at else None
            ),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        """
        Official string representation for debugging and logging.
        """
        return (
            f"<Inventory id={self.id} product_id={self.product_id} "
            f"quantity={self.quantity} threshold={self.low_stock_threshold}>"
        )
