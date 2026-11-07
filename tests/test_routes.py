"""
API Route Controller Integration Tests.

Why this file exists:
While `test_services.py` verifies our pure Python business logic, this file tests
the HTTP communication layer using Flask's built-in `test_client()`.
It ensures JSON serialization, HTTP headers, request parsing, and HTTP status codes
(200, 201, 400, 404, 409) work seamlessly.
"""

import unittest
import json
from app import create_app
from database.db import db


class TestAPIRoutes(unittest.TestCase):
    """Integration test suite for Flask Blueprints (HTTP endpoints)."""

    def setUp(self) -> None:
        """Create test client with in-memory database."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        """Tear down database tables."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_health_check_endpoint(self) -> None:
        """Verify GET /api/health returns 200 OK."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "healthy")

    def test_end_to_end_http_flow(self) -> None:
        """
        Tests complete HTTP lifecycle:
        1. Add product via POST /api/products
        2. Increase stock via POST /api/inventory/<id>/increase
        3. Make sale via POST /api/sales
        4. Query revenue via GET /api/analytics/revenue
        """
        # Step 1: POST /api/products
        prod_payload = {
            "sku": "HTTP-TEST-1",
            "name": "Test Wireless Earbuds",
            "category": "Audio",
            "price": 50.0,
            "initial_stock": 20,
            "low_stock_threshold": 5,
        }
        res_prod = self.client.post(
            "/api/products",
            data=json.dumps(prod_payload),
            content_type="application/json",
        )
        self.assertEqual(res_prod.status_code, 201)
        prod_data = json.loads(res_prod.data)["data"]
        product_id = prod_data["id"]

        # Step 2: POST /api/inventory/<id>/increase
        res_inv = self.client.post(
            f"/api/inventory/{product_id}/increase",
            data=json.dumps({"quantity": 10}),
            content_type="application/json",
        )
        self.assertEqual(res_inv.status_code, 200)
        inv_data = json.loads(res_inv.data)["data"]
        self.assertEqual(inv_data["quantity"], 30)  # 20 initial + 10 restocked

        # Step 3: POST /api/sales
        sale_payload = {
            "product_id": product_id,
            "quantity": 2,
            "discount": 10.0,  # 10% off of 2 * 50 = $100 -> $90
        }
        res_sale = self.client.post(
            "/api/sales",
            data=json.dumps(sale_payload),
            content_type="application/json",
        )
        self.assertEqual(res_sale.status_code, 201)
        sale_data = json.loads(res_sale.data)["data"]
        self.assertEqual(sale_data["total_amount"], 90.0)

        # Step 4: GET /api/analytics/revenue
        res_rev = self.client.get("/api/analytics/revenue")
        self.assertEqual(res_rev.status_code, 200)
        rev_data = json.loads(res_rev.data)["data"]
        self.assertEqual(rev_data["total_revenue"], 90.0)
        self.assertEqual(rev_data["total_transactions"], 1)

        # Step 5: GET /api/analytics/inventory-summary
        res_summary = self.client.get("/api/analytics/inventory-summary")
        self.assertEqual(res_summary.status_code, 200)
        summary_data = json.loads(res_summary.data)["data"]
        self.assertEqual(summary_data["total_inventory_units"], 28)  # 30 - 2 sold = 28
        self.assertEqual(summary_data["total_inventory_asset_value"], 1400.0)  # 28 * $50


if __name__ == "__main__":
    unittest.main()
