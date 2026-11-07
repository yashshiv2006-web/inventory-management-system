"""
Purchase Order Model Module.

Purpose:
Represents wholesale inventory replenishment orders placed with suppliers for products.

Why this file exists:
In retail supply chains, when stock drops below threshold levels, store managers issue
Purchase Orders (POs) to wholesale vendors. This model records procurement costs,
quantities ordered, fulfillment status, and delivery audit timestamps.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from database.db import db


class PurchaseOrder(db.Model):
    """
    Represents a wholesale purchase order contract placed with an external supplier.

    Attributes:
        id (int): Primary key.
        order_number (str): Unique human-readable PO number (e.g. 'PO-2026-1001').
        product_id (int): Foreign key referencing the ordered Product.
        supplier_id (int): Foreign key referencing the supplying wholesale Vendor.
        quantity (int): Number of wholesale units ordered.
        unit_cost (float): Wholesale cost per unit paid to the supplier.
        total_cost (float): Calculated expenditure: quantity * unit_cost.
        status (str): Procurement state ('PENDING', 'RECEIVED', 'CANCELLED').
        order_date (datetime): Timestamp when the PO was placed.
        delivery_date (datetime): Timestamp when shipment was received at warehouse.
    """

    __tablename__ = "purchase_orders"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Unique Purchase Order Code
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)

    # Foreign Key linking to Product (Product can have Many Purchase Orders)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Foreign Key linking to Supplier (Supplier supplies Many Purchase Orders)
    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey("suppliers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Quantity ordered
    quantity = db.Column(db.Integer, nullable=False)

    # Wholesale unit price
    unit_cost = db.Column(db.Float, nullable=False)

    # Total order amount = quantity * unit_cost
    total_cost = db.Column(db.Float, nullable=False)

    # Order fulfillment status
    status = db.Column(db.String(30), default="PENDING", nullable=False)

    # Procurement timestamps
    order_date = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    delivery_date = db.Column(db.DateTime, nullable=True)

    # --- Relationships ---
    product = db.relationship("Product", back_populates="purchase_orders")
    supplier = db.relationship("Supplier", back_populates="purchase_orders")

    def __init__(
        self,
        order_number: str,
        product_id: int,
        supplier_id: int,
        quantity: int,
        unit_cost: float,
        status: str = "PENDING",
        delivery_date: Optional[datetime] = None,
    ) -> None:
        """
        Constructor to initialize a new PurchaseOrder entity.

        Args:
            order_number (str): Unique PO tracking code.
            product_id (int): Target product ID.
            supplier_id (int): Vendor supplier ID.
            quantity (int): Number of units ordered.
            unit_cost (float): Cost per unit.
            status (str, optional): Order status. Defaults to 'PENDING'.
            delivery_date (datetime, optional): Expected delivery time.
        """
        self.order_number = order_number.strip().upper()
        self.product_id = int(product_id)
        self.supplier_id = int(supplier_id)
        self.quantity = int(quantity)
        self.unit_cost = float(unit_cost)
        self.total_cost = round(float(self.quantity * self.unit_cost), 2)
        self.status = status.strip().upper()
        self.delivery_date = delivery_date

    def to_dict(self) -> Dict[str, Any]:
        """Serializes purchase order into a dictionary for JSON reporting."""
        return {
            "id": self.id,
            "order_number": self.order_number,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else "N/A",
            "product_sku": self.product.sku if self.product else "N/A",
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier.name if self.supplier else "N/A",
            "quantity": self.quantity,
            "unit_cost": round(self.unit_cost, 2),
            "total_cost": round(self.total_cost, 2),
            "status": self.status,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "delivery_date": self.delivery_date.isoformat() if self.delivery_date else None,
        }

    def __repr__(self) -> str:
        return (
            f"<PurchaseOrder id={self.id} po='{self.order_number}' "
            f"qty={self.quantity} total=${self.total_cost} status='{self.status}'>"
        )
