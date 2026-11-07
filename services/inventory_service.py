"""
Inventory Service Module.

Why this file exists:
Inventory management is the core of retail operations. This service isolates
all logic governing physical shelf units, stock replenishments (restocks),
deductions (sales, damages), inventory status evaluations, and proactive
low-stock reorder warnings.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from database.db import db
from models.inventory import Inventory
from models.product import Product
from utils.helpers import (
    ResourceNotFoundError,
    InsufficientStockError,
    ValidationError,
)


class InventoryService:
    """
    Encapsulates all business logic for monitoring, modifying, and auditing inventory levels.
    """

    @staticmethod
    def get_inventory_by_product_id(product_id: int) -> Inventory:
        """
        Helper method to retrieve an inventory record by its associated product ID.

        Args:
            product_id (int): Product primary key.

        Returns:
            Inventory: The associated inventory entity.

        Raises:
            ResourceNotFoundError: If the product or its inventory ledger does not exist.
        """
        inventory = Inventory.query.filter_by(product_id=product_id).first()
        if not inventory:
            # Check if the product even exists to produce an accurate error message
            product_exists = db.session.get(Product, product_id)
            if not product_exists:
                raise ResourceNotFoundError(
                    f"Product with ID {product_id} does not exist."
                )
            # If product exists but inventory record was missing, create a default one
            inventory = Inventory(product_id=product_id, quantity=0)
            db.session.add(inventory)
            db.session.commit()

        return inventory

    @staticmethod
    def increase_stock(product_id: int, quantity: int) -> Inventory:
        """
        Increases the stock quantity for a product (e.g. when receiving a supplier shipment).

        Business Rules:
        1. Quantity to add must be strictly greater than 0.
        2. Must update the `last_restocked_at` timestamp.
        3. All database updates must be committed atomically.

        Args:
            product_id (int): ID of the product being restocked.
            quantity (int): Units to add to current stock.

        Returns:
            Inventory: The updated Inventory record.

        Raises:
            ValidationError: If quantity is <= 0.
            ResourceNotFoundError: If the product does not exist.
        """
        if quantity <= 0:
            raise ValidationError("Stock increase quantity must be strictly greater than zero.")

        inventory = InventoryService.get_inventory_by_product_id(product_id)

        try:
            # Increase the stock balance
            inventory.quantity += int(quantity)

            # Record the exact restock timestamp
            inventory.last_restocked_at = datetime.now(timezone.utc)

            # Commit the transaction to the database
            db.session.commit()
            return inventory

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def decrease_stock(product_id: int, quantity: int) -> Inventory:
        """
        Decreases stock for a product (used during sales transactions or stock damage/shrinkage).

        Business Rules:
        1. Quantity to deduct must be strictly greater than 0.
        2. Current inventory must have sufficient units available.
        3. Negative inventory balances are strictly prohibited in retail accounting!

        Args:
            product_id (int): ID of the product.
            quantity (int): Units to deduct.

        Returns:
            Inventory: The updated Inventory record.

        Raises:
            ValidationError: If quantity is <= 0.
            InsufficientStockError: If requested quantity exceeds current stock.
            ResourceNotFoundError: If the product does not exist.
        """
        if quantity <= 0:
            raise ValidationError("Stock deduction quantity must be strictly greater than zero.")

        inventory = InventoryService.get_inventory_by_product_id(product_id)

        # Crucial Business Check: Prevent negative stock
        if inventory.quantity < quantity:
            product_name = inventory.product.name if inventory.product else f"ID {product_id}"
            raise InsufficientStockError(
                f"Cannot fulfill order! Insufficient stock for '{product_name}'. "
                f"Available: {inventory.quantity}, Requested: {quantity}."
            )

        try:
            # Deduct the units
            inventory.quantity -= int(quantity)

            # Commit the updated balance
            db.session.commit()
            return inventory

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def check_stock(product_id: int) -> Dict[str, Any]:
        """
        Checks real-time inventory levels, health status, and alert indicators for a product.

        Args:
            product_id (int): ID of the product to query.

        Returns:
            Dict[str, Any]: Comprehensive stock report dictionary.

        Raises:
            ResourceNotFoundError: If product is not found.
        """
        inventory = InventoryService.get_inventory_by_product_id(product_id)
        return inventory.to_dict()

    @staticmethod
    def get_low_stock_products(threshold: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Identifies all products in the catalog whose current stock is at or below
        their low-stock threshold (or an optional override threshold).

        This enables store managers to generate proactive supplier reorder lists.

        Args:
            threshold (Optional[int]): Custom threshold override. If None, uses each
                                       product's own individual configured threshold.

        Returns:
            List[Dict[str, Any]]: List of low-stock alert dictionaries.
        """
        if threshold is not None:
            # Query products whose quantity is less than or equal to the custom threshold
            records = (
                Inventory.query.filter(Inventory.quantity <= int(threshold))
                .order_by(Inventory.quantity.asc())
                .all()
            )
        else:
            # Query products whose quantity is less than or equal to their individual threshold
            records = (
                Inventory.query.filter(Inventory.quantity <= Inventory.low_stock_threshold)
                .order_by(Inventory.quantity.asc())
                .all()
            )

        # Convert each record into a friendly alert payload
        low_stock_list: List[Dict[str, Any]] = []
        for inv in records:
            low_stock_list.append({
                "product_id": inv.product_id,
                "product_name": inv.product.name if inv.product else "Unknown",
                "product_sku": inv.product.sku if inv.product else "Unknown",
                "category": inv.product.category if inv.product else "Unknown",
                "current_stock": inv.quantity,
                "threshold": inv.low_stock_threshold,
                "reorder_needed": True,
                "status": inv.get_stock_status(),
            })

        return low_stock_list
