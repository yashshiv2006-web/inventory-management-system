"""
Sales Model Module.

Purpose:
Represents immutable financial point-of-sale customer purchase receipts.

Why this file exists:
In retail accounting, each sale records the exact historical unit price, quantity,
discount percentage, and total revenue at the instant of transaction.
Establishes the 'Product Has Many Sales' relationship.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from database.db import db


class Sale(db.Model):
    """
    Represents an individual customer sales receipt.

    Attributes:
        id (int): Primary key.
        product_id (int): Foreign key linking the sale to the purchased Product.
        quantity (int): Number of units purchased in this transaction.
        unit_price (float): Snapshot of unit retail price at transaction moment.
        discount (float): Applied promotional discount percentage (0 to 100).
        total_amount (float): Calculated final total charge: (qty * price) * (1 - discount/100).
        sale_date (datetime): Transaction timestamp.
    """

    __tablename__ = "sales"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Key linking to Product (Product Has Many Sales)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Transaction details
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

    # Chronological timestamp, indexed for fast date-range analytics
    sale_date = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # --- Relationships ---
    # Bi-directional relationship back to the parent Product
    product = db.relationship("Product", back_populates="sales")

    def __init__(
        self,
        product_id: int,
        quantity: int,
        unit_price: float,
        discount: float,
        total_amount: float,
        sale_date: Optional[datetime] = None,
    ) -> None:
        """Constructor to initialize a new Sale transaction record."""
        self.product_id = int(product_id)
        self.quantity = int(quantity)
        self.unit_price = float(unit_price)
        self.discount = float(discount)
        self.total_amount = round(float(total_amount), 2)
        self.sale_date = sale_date or datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes sale entity into a dictionary for JSON responses."""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else "Deleted Product",
            "product_sku": self.product.sku if self.product else "N/A",
            "quantity": self.quantity,
            "unit_price": round(self.unit_price, 2),
            "discount_percentage": self.discount,
            "total_amount": round(self.total_amount, 2),
            "sale_date": self.sale_date.isoformat() if self.sale_date else None,
        }

    def __repr__(self) -> str:
        return (
            f"<Sale id={self.id} product_id={self.product_id} "
            f"qty={self.quantity} total=${self.total_amount}>"
        )
