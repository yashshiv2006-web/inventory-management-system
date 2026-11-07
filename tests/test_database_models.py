"""
SQLite Database Schema and Relationship Integrity Tests.

Purpose:
Verifies that:
1. All 5 required tables (users, suppliers, products, sales, purchase_orders)
   are created in SQLite.
2. Foreign key constraints are enforced (e.g. deleting a product cascades to its sales).
3. Bi-directional SQLAlchemy relationships function as designed.
"""

import unittest
from app import create_app
from database.db import db
from models.user import User
from models.supplier import Supplier
from models.product import Product
from models.sales import Sale
from models.purchase_order import PurchaseOrder


class TestDatabaseSchema(unittest.TestCase):
    """Unit test suite for SQLite schema and ORM entity relationships."""

    def setUp(self) -> None:
        """Initialize in-memory testing database with foreign keys enabled."""
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        """Tear down database."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_product_relationship(self) -> None:
        """Test User -> Creates Products (1-to-Many)."""
        user = User(username="manager_jane", email="jane@store.com")
        db.session.add(user)
        db.session.commit()

        product = Product(
            sku="LPT-001",
            name="Ultrabook Laptop",
            category="Computers",
            price=899.99,
            created_by_user_id=user.id,
        )
        db.session.add(product)
        db.session.commit()

        # Verify bi-directional relationship
        self.assertEqual(len(user.products), 1)
        self.assertEqual(user.products[0].name, "Ultrabook Laptop")
        self.assertEqual(product.created_by_user.username, "manager_jane")

    def test_supplier_product_relationship(self) -> None:
        """Test Supplier -> Supplies Many Products (1-to-Many)."""
        supplier = Supplier(
            name="Alpha Distributors",
            contact_name="Bob Ray",
            email="orders@alphadist.com",
            phone="555-0192",
            category="Electronics",
        )
        db.session.add(supplier)
        db.session.commit()

        prod1 = Product(sku="SP-01", name="Product 1", category="Electronics", price=10.0, supplier_id=supplier.id)
        prod2 = Product(sku="SP-02", name="Product 2", category="Electronics", price=20.0, supplier_id=supplier.id)
        db.session.add_all([prod1, prod2])
        db.session.commit()

        self.assertEqual(len(supplier.products), 2)
        self.assertEqual(prod1.supplier.name, "Alpha Distributors")

    def test_product_sales_relationship(self) -> None:
        """Test Product -> Has Many Sales (1-to-Many)."""
        product = Product(sku="MOU-99", name="Optical Mouse", category="Peripherals", price=15.0)
        db.session.add(product)
        db.session.commit()

        sale1 = Sale(product_id=product.id, quantity=2, unit_price=15.0, discount=0.0, total_amount=30.0)
        sale2 = Sale(product_id=product.id, quantity=1, unit_price=15.0, discount=10.0, total_amount=13.5)
        db.session.add_all([sale1, sale2])
        db.session.commit()

        self.assertEqual(len(product.sales), 2)
        self.assertEqual(sale1.product.name, "Optical Mouse")

    def test_purchase_order_creation_and_linking(self) -> None:
        """Test Product -> Can Have Many Purchase Orders and Supplier -> POs."""
        supplier = Supplier(
            name="Hardware Corp",
            contact_name="Ken Adams",
            email="ken@hwcorp.com",
            phone="555-4321",
            category="Hardware",
        )
        db.session.add(supplier)
        db.session.commit()

        product = Product(sku="HD-01", name="Hammer Drill", category="Hardware", price=120.0, supplier_id=supplier.id)
        db.session.add(product)
        db.session.commit()

        po = PurchaseOrder(
            order_number="PO-2026-9001",
            product_id=product.id,
            supplier_id=supplier.id,
            quantity=50,
            unit_cost=75.0,
        )
        db.session.add(po)
        db.session.commit()

        self.assertEqual(po.total_cost, 3750.0)
        self.assertEqual(po.product.name, "Hammer Drill")
        self.assertEqual(po.supplier.name, "Hardware Corp")
        self.assertEqual(len(product.purchase_orders), 1)
        self.assertEqual(len(supplier.purchase_orders), 1)

    def test_cascade_delete_integrity(self) -> None:
        """Test that deleting a product automatically removes its sales and purchase orders."""
        supplier = Supplier(name="Test Sup", contact_name="Tom", email="tom@sup.com", phone="123", category="General")
        db.session.add(supplier)
        db.session.commit()

        product = Product(sku="DEL-ITEM", name="To Delete", category="General", price=5.0, supplier_id=supplier.id)
        db.session.add(product)
        db.session.commit()

        sale = Sale(product_id=product.id, quantity=1, unit_price=5.0, discount=0.0, total_amount=5.0)
        po = PurchaseOrder(order_number="PO-DEL-01", product_id=product.id, supplier_id=supplier.id, quantity=10, unit_cost=3.0)
        db.session.add_all([sale, po])
        db.session.commit()

        # Delete the product
        db.session.delete(product)
        db.session.commit()

        # Verify child records in sales and purchase_orders are cleaned up
        self.assertEqual(Sale.query.filter_by(product_id=product.id).count(), 0)
        self.assertEqual(PurchaseOrder.query.filter_by(product_id=product.id).count(), 0)


if __name__ == "__main__":
    unittest.main()
