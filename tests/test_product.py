"""
Product Service and Entity Unit Tests.

Purpose:
Verifies catalog operations, unique SKU constraints, and price validation.
"""

import unittest
from app import create_app
from database.db import db
from services.product_service import ProductService
from utils.helpers import DuplicateResourceError, ValidationError


class TestProductOperations(unittest.TestCase):
    """Unit test suite for ProductService."""

    def setUp(self) -> None:
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_product_validation(self) -> None:
        """Verifies that non-positive prices raise ValidationError."""
        with self.assertRaises(ValidationError):
            ProductService.add_product(
                name="Bad Price Item",
                price=-10.0,
                category="General",
                sku="BAD-01",
            )

    def test_sku_uniqueness(self) -> None:
        """Verifies duplicate SKU rejection."""
        ProductService.add_product(name="P1", price=10.0, category="A", sku="SKU-UNIQ")
        with self.assertRaises(DuplicateResourceError):
            ProductService.add_product(name="P2", price=15.0, category="B", sku="SKU-UNIQ")


if __name__ == "__main__":
    unittest.main()
