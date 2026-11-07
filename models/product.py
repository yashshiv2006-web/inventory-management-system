"""
Product Model Module.

Purpose:
Represents a retail item in the catalog, establishing core relationships between
Users, Suppliers, Sales, Purchase Orders, and Inventory.

Why this file exists:
The Product model is the central entity in retail database architecture.
Relationships modeled:
1. User -> Creates Products (Foreign Key: created_by_user_id)
2. Supplier -> Supplies Many Products (Foreign Key: supplier_id)
3. Product -> Has Many Sales (1-to-Many relationship)
4. Product -> Can Have Many Purchase Orders (1-to-Many relationship)
5. Product -> Inventory (1-to-1 ledger relationship)
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from database.db import db


class Product(db.Model):
    """
    Represents a retail catalog product.

    Attributes:
        id (int): Primary key.
        sku (str): Unique barcode / Stock Keeping Unit.
        name (str): Product display name.
        category (str): Product category.
        price (float): Current unit retail selling price.
        description (str): Detailed product specifications.
        created_by_user_id (int): Foreign Key referencing the User who registered the product.
        supplier_id (int): Foreign Key referencing the wholesale Supplier.
        created_at (datetime): Creation audit timestamp.
        updated_at (datetime): Last modification timestamp.
    """

    __tablename__ = "products"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # SKU: Must be unique and indexed
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)

    # Core attributes
    name = db.Column(db.String(120), nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True, default="")

    # Foreign Key 1: User who created the product (User -> Creates Products)
    created_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Foreign Key 2: Wholesale Supplier (Supplier -> Supplies Many Products)
    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey("suppliers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Timestamps
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Relationships ---
    # Relationship with User:
    created_by_user = db.relationship("User", back_populates="products")

    # Relationship with Supplier:
    supplier = db.relationship("Supplier", back_populates="products")

    # Relationship with Sales: Product -> Has Many Sales
    sales = db.relationship(
        "Sale",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy=True,
    )

    # Relationship with Purchase Orders: Product -> Can Have Many Purchase Orders
    purchase_orders = db.relationship(
        "PurchaseOrder",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy=True,
    )

    # Relationship with Inventory (1-to-1):
    inventory = db.relationship(
        "Inventory",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __init__(
        self,
        sku: str,
        name: str,
        category: str,
        price: float,
        description: str = "",
        created_by_user_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
    ) -> None:
        """Constructor to initialize a Product instance."""
        self.sku = sku.strip().upper()
        self.name = name.strip()
        self.category = category.strip()
        self.price = float(price)
        self.description = description.strip() if description else ""
        self.created_by_user_id = created_by_user_id
        self.supplier_id = supplier_id

    def to_dict(self, include_inventory: bool = True) -> Dict[str, Any]:
        """Serializes Product entity to a Python dictionary for JSON responses."""
        data: Dict[str, Any] = {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "category": self.category,
            "price": round(self.price, 2),
            "description": self.description,
            "created_by_user_id": self.created_by_user_id,
            "created_by_username": self.created_by_user.username if self.created_by_user else None,
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier.name if self.supplier else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_inventory and self.inventory:
            data["current_stock"] = self.inventory.quantity
            data["low_stock_threshold"] = self.inventory.low_stock_threshold
            data["is_low_stock"] = self.inventory.is_low_stock()
        elif include_inventory:
            data["current_stock"] = 0
            data["low_stock_threshold"] = 10
            data["is_low_stock"] = True

        return data

    def __repr__(self) -> str:
        return f"<Product id={self.id} sku='{self.sku}' name='{self.name}' price={self.price}>"
