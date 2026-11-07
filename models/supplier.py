"""
Supplier Model Module.

Purpose:
Represents wholesale vendor organizations that supply products and fulfill purchase orders.

Why this file exists:
In retail stock management, products originate from authorized suppliers.
This model establishes a 1-to-Many relationship with Products ('Supplier Supplies Many Products')
and a 1-to-Many relationship with Purchase Orders.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from database.db import db


class Supplier(db.Model):
    """
    Represents a wholesale vendor or manufacturer supplying retail goods.

    Attributes:
        id (int): Primary key.
        name (str): Company or vendor business name.
        contact_name (str): Representative contact person.
        email (str): Business email address.
        phone (str): Contact phone number.
        category (str): Primary category of goods supplied (e.g. 'Electronics').
        address (str): Physical address or distribution warehouse.
        rating (float): Vendor reliability score (1.0 to 5.0).
        created_at (datetime): Registration timestamp.
    """

    __tablename__ = "suppliers"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Unique vendor name
    name = db.Column(db.String(120), nullable=False, unique=True, index=True)

    # Contact details
    contact_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    address = db.Column(db.String(200), nullable=True, default="")
    rating = db.Column(db.Float, default=4.5)

    # Audit timestamp
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # --- Relationships ---
    # 1-to-Many relationship: One Supplier Supplies Many Products
    products = db.relationship(
        "Product",
        back_populates="supplier",
        lazy=True,
    )

    # 1-to-Many relationship: One Supplier can have Many Purchase Orders
    purchase_orders = db.relationship(
        "PurchaseOrder",
        back_populates="supplier",
        lazy=True,
    )

    def __init__(
        self,
        name: str,
        contact_name: str,
        email: str,
        phone: str,
        category: str,
        address: str = "",
        rating: float = 4.5,
    ) -> None:
        """Constructor to initialize a wholesale Supplier."""
        self.name = name.strip()
        self.contact_name = contact_name.strip()
        self.email = email.strip()
        self.phone = phone.strip()
        self.category = category.strip()
        self.address = address.strip() if address else ""
        self.rating = float(rating)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes supplier entity to a Python dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone": self.phone,
            "category": self.category,
            "address": self.address,
            "rating": round(self.rating, 1),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "products_count": len(self.products) if self.products else 0,
        }

    def __repr__(self) -> str:
        return f"<Supplier id={self.id} name='{self.name}' category='{self.category}'>"
