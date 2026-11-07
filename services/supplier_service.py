"""
Supplier Service Module.

Why this file exists:
Manages wholesale vendor information, supply categories, and contact directories.
Used by the Supplier Table view and replenishment planning features.
"""

from typing import List, Dict, Any, Optional
from database.db import db
from models.supplier import Supplier
from utils.helpers import ResourceNotFoundError, DuplicateResourceError, ValidationError


class SupplierService:
    """Encapsulates business operations for managing retail supplier partners."""

    @staticmethod
    def list_suppliers() -> List[Supplier]:
        """Returns all registered suppliers ordered by name."""
        return Supplier.query.order_by(Supplier.name.asc()).all()

    @staticmethod
    def get_supplier_by_id(supplier_id: int) -> Supplier:
        """Fetches a single supplier by ID."""
        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            raise ResourceNotFoundError(f"Supplier with ID {supplier_id} not found.")
        return supplier

    @staticmethod
    def add_supplier(
        name: str,
        contact_name: str,
        email: str,
        phone: str,
        category: str,
        address: str = "",
        rating: float = 4.5,
    ) -> Supplier:
        """Registers a new supplier in the system."""
        clean_name = str(name).strip()
        if not clean_name:
            raise ValidationError("Supplier name cannot be empty.")

        existing = Supplier.query.filter_by(name=clean_name).first()
        if existing:
            raise DuplicateResourceError(f"Supplier '{clean_name}' already exists.")

        supplier = Supplier(
            name=clean_name,
            contact_name=contact_name,
            email=email,
            phone=phone,
            category=category,
            address=address,
            rating=rating,
        )
        db.session.add(supplier)
        db.session.commit()
        return supplier
