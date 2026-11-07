"""
Sales Service and Financial Ledger Unit Tests.

Purpose:
Verifies sale amount calculations, discounts, and inventory auto-deduction.
"""

import unittest
from app import create_app
from database.db import db
from services.product_service import ProductService
from services.sales_service import SalesService
from services.inventory_service import InventoryService


class TestSalesOperations(unittest.TestCase):
    """Unit test suite for SalesService."""

    def setUp(self) -> None:
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.prod = ProductService.add_product(
            sku="SALE-T1", name="Retail Good", category="Goods", price=100.0, initial_stock=20
        )

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_sale_creation_and_stock_reduction(self) -> None:
        """Verifies sale creation with discount and stock reduction."""
        sale = SalesService.create_sale(self.prod.id, quantity=4, discount=15.0)
        # Expected: 4 * $100 = $400 - 15% ($60) = $340
        self.assertEqual(sale.total_amount, 340.0)

        # Check stock is 20 - 4 = 16
        stock = InventoryService.check_stock(self.prod.id)
        self.assertEqual(stock["quantity"], 16)


if __name__ == "__main__":
    unittest.main()
