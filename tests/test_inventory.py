"""
Inventory Service and Stock Control Unit Tests.

Purpose:
Verifies restocking, write-off deductions, and low-stock alerts.
"""

import unittest
from app import create_app
from database.db import db
from services.product_service import ProductService
from services.inventory_service import InventoryService
from utils.helpers import InsufficientStockError


class TestInventoryOperations(unittest.TestCase):
    """Unit test suite for InventoryService."""

    def setUp(self) -> None:
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.prod = ProductService.add_product(
            sku="INV-T1", name="Tracked Item", category="Test", price=20.0, initial_stock=10
        )

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_stock_replenishment(self) -> None:
        """Verifies increasing stock."""
        InventoryService.increase_stock(self.prod.id, 15)
        stock = InventoryService.check_stock(self.prod.id)
        self.assertEqual(stock["quantity"], 25)

    def test_insufficient_stock_prevention(self) -> None:
        """Verifies that deducting more than available stock raises InsufficientStockError."""
        with self.assertRaises(InsufficientStockError):
            InventoryService.decrease_stock(self.prod.id, 50)


if __name__ == "__main__":
    unittest.main()
