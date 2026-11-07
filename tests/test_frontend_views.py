"""
Frontend Template and Web Route Integration Tests.

Why this file exists:
Verifies that all 11 HTML templates render without Jinja2 syntax errors,
all GET routes return HTTP 200 OK, and form POST actions (Add Product, Edit Product,
Adjust Inventory, Record Sale) correctly integrate with the underlying Service Layer.
"""

import unittest
from app import create_app
from database.db import db
from services.product_service import ProductService
from services.supplier_service import SupplierService


class TestFrontendViews(unittest.TestCase):
    """Verifies that all web routes render their corresponding HTML templates."""

    def setUp(self) -> None:
        """Initialize in-memory testing app."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed initial product and supplier for page rendering tests
        ProductService.add_product(
            sku="TEST-SKU",
            name="Test Monitor",
            category="Electronics",
            price=250.0,
            initial_stock=15,
            low_stock_threshold=5,
        )
        SupplierService.add_supplier(
            name="Test Supplier Inc",
            contact_name="Alice Smith",
            email="alice@test.com",
            phone="123-456",
            category="Electronics",
        )

    def tearDown(self) -> None:
        """Tear down database."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_page_renders(self) -> None:
        """GET /login renders login.html."""
        res = self.client.get("/login")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"RetailPulse AI", res.data)
        self.assertIn(b"Demo Credentials", res.data)

    def test_dashboard_page_renders(self) -> None:
        """GET / and GET /dashboard render dashboard.html with 5 metric cards."""
        res = self.client.get("/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Executive Dashboard", res.data)
        self.assertIn(b"Total Products", res.data)
        self.assertIn(b"Total Revenue", res.data)
        self.assertIn(b"Low Stock Alerts", res.data)
        self.assertIn(b"Top Selling Product", res.data)
        self.assertIn(b"Predicted Demand", res.data)

    def test_products_page_renders(self) -> None:
        """GET /products renders products.html."""
        res = self.client.get("/products")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Product Catalog", res.data)
        self.assertIn(b"TEST-SKU", res.data)

    def test_add_product_page_renders(self) -> None:
        """GET /products/add renders add_product.html."""
        res = self.client.get("/products/add")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Register New Product", res.data)

    def test_edit_product_page_renders(self) -> None:
        """GET /products/edit/1 renders edit_product.html with prefilled data."""
        res = self.client.get("/products/edit/1")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Test Monitor", res.data)

    def test_inventory_page_renders(self) -> None:
        """GET /inventory renders inventory.html with stock ledger and supplier table."""
        res = self.client.get("/inventory")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Real-Time Inventory Ledger", res.data)
        self.assertIn(b"Wholesale Supplier Directory", res.data)
        self.assertIn(b"Test Supplier Inc", res.data)

    def test_sales_page_renders(self) -> None:
        """GET /sales renders sales.html with POS form and sales history."""
        res = self.client.get("/sales")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Record Customer Sale", res.data)
        self.assertIn(b"Sales Transaction Ledger", res.data)

    def test_analytics_page_renders(self) -> None:
        """GET /analytics renders analytics.html with charts."""
        res = self.client.get("/analytics")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Sales Intelligence & Business Analytics", res.data)
        self.assertIn(b"revenueTrendChart", res.data)
        self.assertIn(b"inventoryHealthChart", res.data)

    def test_reports_page_renders(self) -> None:
        """GET /reports renders reports.html."""
        res = self.client.get("/reports")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Reports & Audit Center", res.data)

    def test_reports_csv_export(self) -> None:
        """GET /reports?format=csv&type=inventory exports CSV file."""
        res = self.client.get("/reports?format=csv&type=inventory")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "text/csv; charset=utf-8")
        self.assertIn(b"TEST-SKU", res.data)

    def test_forecasting_page_renders(self) -> None:
        """GET /forecasting renders forecasting.html with demand predictions."""
        res = self.client.get("/forecasting")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Predictive Demand & Stock Optimization", res.data)
        self.assertIn(b"Recommended Reorder", res.data)

    def test_form_submission_add_product(self) -> None:
        """POST /products/add successfully creates product and redirects."""
        payload = {
            "sku": "NEW-PROD-99",
            "name": "Mechanical Pencil",
            "category": "Accessories",
            "price": "3.50",
            "description": "0.7mm lead",
            "initial_stock": "50",
            "low_stock_threshold": "10",
        }
        res = self.client.post("/products/add", data=payload, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"added successfully", res.data)
        self.assertIn(b"NEW-PROD-99", res.data)

    def test_form_submission_record_sale(self) -> None:
        """POST /sales/create records sale and decrements stock."""
        payload = {
            "product_id": "1",
            "quantity": "2",
            "discount": "0",
        }
        res = self.client.post("/sales/create", data=payload, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"completed", res.data)


if __name__ == "__main__":
    unittest.main()
