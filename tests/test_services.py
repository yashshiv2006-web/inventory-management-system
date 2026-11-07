"""
Unit and Integration Tests for Retail Stock Optimization and Sales Intelligence Platform.

Why this file exists:
In enterprise software engineering, unit and integration tests verify that business
logic functions correctly under both expected conditions and edge cases (e.g. stockout,
duplicate SKU, invalid input).

These tests run against an in-memory SQLite database (`TestingConfig`) so they execute
in milliseconds without modifying or leaving behind test records in the production database.
"""

import unittest
from app import create_app
from database.db import db
from services.product_service import ProductService
from services.inventory_service import InventoryService
from services.sales_service import SalesService
from services.analytics_service import AnalyticsService
from utils.helpers import (
    ResourceNotFoundError,
    InsufficientStockError,
    DuplicateResourceError,
    ValidationError,
)


class TestRetailPlatformBackend(unittest.TestCase):
    """
    Test suite covering ProductService, InventoryService, SalesService,
    AnalyticsService, and end-to-end integration flows.
    """

    def setUp(self) -> None:
        """Executed before EVERY individual test method."""
        # Create Flask app using isolated in-memory test configuration
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create fresh SQLite tables in memory
        db.create_all()

    def tearDown(self) -> None:
        """Executed after EVERY individual test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ==========================================================================
    # 1. Product Service Tests
    # ==========================================================================

    def test_add_product_success(self) -> None:
        """Test adding a product creates both Product and Inventory records."""
        product = ProductService.add_product(
            name="Mechanical Keyboard",
            price=75.0,
            category="Peripherals",
            sku="KB-001",
            initial_stock=20,
            low_stock_threshold=5,
        )

        self.assertIsNotNone(product.id)
        self.assertEqual(product.name, "Mechanical Keyboard")
        self.assertEqual(product.sku, "KB-001")
        self.assertEqual(product.price, 75.0)

        # Verify linked inventory record was automatically created
        stock_info = InventoryService.check_stock(product.id)
        self.assertEqual(stock_info["quantity"], 20)
        self.assertEqual(stock_info["low_stock_threshold"], 5)
        self.assertEqual(stock_info["status"], "IN_STOCK")

    def test_add_product_duplicate_sku(self) -> None:
        """Test that duplicate SKUs raise DuplicateResourceError."""
        ProductService.add_product(
            name="Item A", price=10.0, category="General", sku="DUP-100"
        )

        with self.assertRaises(DuplicateResourceError):
            ProductService.add_product(
                name="Item B", price=15.0, category="General", sku="DUP-100"
            )

    def test_update_product(self) -> None:
        """Test updating product fields (name and price)."""
        product = ProductService.add_product(
            name="Old Name", price=20.0, category="General", sku="UPD-001"
        )

        updated = ProductService.update_product(
            product.id, name="New Name", price=25.50
        )
        self.assertEqual(updated.name, "New Name")
        self.assertEqual(updated.price, 25.50)

    def test_search_product(self) -> None:
        """Test searching products by name or category."""
        ProductService.add_product(
            name="Wireless Mouse", price=20.0, category="Electronics", sku="MOU-01"
        )
        ProductService.add_product(
            name="Gaming Chair", price=150.0, category="Furniture", sku="CHR-01"
        )

        mouse_results = ProductService.search_product("mouse")
        self.assertEqual(len(mouse_results), 1)
        self.assertEqual(mouse_results[0].sku, "MOU-01")

        furn_results = ProductService.search_product("furniture")
        self.assertEqual(len(furn_results), 1)
        self.assertEqual(furn_results[0].sku, "CHR-01")

    def test_delete_product(self) -> None:
        """Test deleting product removes product and inventory."""
        product = ProductService.add_product(
            name="Temp Item", price=5.0, category="Misc", sku="DEL-01"
        )
        prod_id = product.id

        self.assertTrue(ProductService.delete_product(prod_id))

        with self.assertRaises(ResourceNotFoundError):
            ProductService.get_product_by_id(prod_id)

    # ==========================================================================
    # 2. Inventory Service Tests
    # ==========================================================================

    def test_increase_and_decrease_stock(self) -> None:
        """Test replenishing and deducting stock."""
        product = ProductService.add_product(
            name="Widget", price=10.0, category="Hardware", sku="WID-01", initial_stock=10
        )

        # Increase stock by 15 -> total should be 25
        InventoryService.increase_stock(product.id, 15)
        stock = InventoryService.check_stock(product.id)
        self.assertEqual(stock["quantity"], 25)

        # Decrease stock by 5 -> total should be 20
        InventoryService.decrease_stock(product.id, 5)
        stock = InventoryService.check_stock(product.id)
        self.assertEqual(stock["quantity"], 20)

    def test_decrease_stock_insufficient_error(self) -> None:
        """Test decreasing more stock than available raises InsufficientStockError."""
        product = ProductService.add_product(
            name="Gadget", price=15.0, category="Hardware", sku="GAD-01", initial_stock=3
        )

        with self.assertRaises(InsufficientStockError):
            InventoryService.decrease_stock(product.id, 10)

    def test_get_low_stock_products(self) -> None:
        """Test identifying low stock products."""
        # Product with 2 units (threshold is 5) -> should be flagged as low stock
        ProductService.add_product(
            name="Low Stock Item",
            price=12.0,
            category="Hardware",
            sku="LOW-01",
            initial_stock=2,
            low_stock_threshold=5,
        )
        # Product with 50 units (threshold is 5) -> normal
        ProductService.add_product(
            name="Normal Item",
            price=12.0,
            category="Hardware",
            sku="NORM-01",
            initial_stock=50,
            low_stock_threshold=5,
        )

        alerts = InventoryService.get_low_stock_products()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["product_sku"], "LOW-01")

    # ==========================================================================
    # 3. Sales Service Tests
    # ==========================================================================

    def test_calculate_sale_amount(self) -> None:
        """Test discount and total amount math."""
        # 10 units at $10.00 each = $100.00 with 0% discount
        self.assertEqual(
            SalesService.calculate_sale_amount(unit_price=10.0, quantity=10, discount=0.0),
            100.0,
        )
        # 2 units at $50.00 each = $100.00 with 10% discount = $90.00
        self.assertEqual(
            SalesService.calculate_sale_amount(unit_price=50.0, quantity=2, discount=10.0),
            90.0,
        )

    def test_create_sale_decrements_inventory(self) -> None:
        """Test creating a sale automatically deducts inventory."""
        product = ProductService.add_product(
            name="Headphones",
            price=100.0,
            category="Audio",
            sku="HP-01",
            initial_stock=10,
        )

        sale = SalesService.create_sale(
            product_id=product.id, quantity=3, discount=10.0
        )

        # Total amount: 3 * $100 = $300 - 10% ($30) = $270
        self.assertEqual(sale.total_amount, 270.0)
        self.assertEqual(sale.unit_price, 100.0)

        # Inventory should now be 10 - 3 = 7 units
        stock = InventoryService.check_stock(product.id)
        self.assertEqual(stock["quantity"], 7)

    def test_create_sale_fails_if_out_of_stock(self) -> None:
        """Test creating a sale for more units than in stock raises InsufficientStockError."""
        product = ProductService.add_product(
            name="Limited Edition Watch",
            price=500.0,
            category="Luxury",
            sku="WATCH-01",
            initial_stock=1,
        )

        with self.assertRaises(InsufficientStockError):
            SalesService.create_sale(product_id=product.id, quantity=5)

        # Inventory must remain intact at 1
        stock = InventoryService.check_stock(product.id)
        self.assertEqual(stock["quantity"], 1)

    # ==========================================================================
    # 4. Analytics Service Tests
    # ==========================================================================

    def test_analytics_revenue_and_top_selling(self) -> None:
        """Test revenue aggregation and top selling rankings."""
        p1 = ProductService.add_product(
            name="USB-C Hub", price=40.0, category="Accessories", sku="HUB-01", initial_stock=50
        )
        p2 = ProductService.add_product(
            name="HDMI Cable", price=15.0, category="Accessories", sku="HDMI-01", initial_stock=50
        )

        # Record sales
        SalesService.create_sale(product_id=p1.id, quantity=5)  # $200
        SalesService.create_sale(product_id=p2.id, quantity=10) # $150

        # Revenue Analytics
        rev_metrics = AnalyticsService.calculate_total_revenue()
        self.assertEqual(rev_metrics["total_revenue"], 350.0)
        self.assertEqual(rev_metrics["total_transactions"], 2)
        self.assertEqual(rev_metrics["total_units_sold"], 15)
        self.assertEqual(rev_metrics["average_order_value"], 175.0)

        # Top Selling Products (ordered by units sold: HDMI Cable sold 10, USB-C Hub sold 5)
        top_sellers = AnalyticsService.get_top_selling_products(limit=5)
        self.assertEqual(len(top_sellers), 2)
        self.assertEqual(top_sellers[0]["product_name"], "HDMI Cable")
        self.assertEqual(top_sellers[0]["units_sold"], 10)
        self.assertEqual(top_sellers[1]["product_name"], "USB-C Hub")
        self.assertEqual(top_sellers[1]["units_sold"], 5)

    def test_inventory_summary_valuation(self) -> None:
        """Test inventory asset value calculation: quantity * price."""
        ProductService.add_product(
            name="Item 1", price=10.0, category="A", sku="I1", initial_stock=10
        )  # Valuation: 10 * 10 = $100
        ProductService.add_product(
            name="Item 2", price=50.0, category="B", sku="I2", initial_stock=4
        )  # Valuation: 4 * 50 = $200

        summary = AnalyticsService.get_inventory_summary()
        self.assertEqual(summary["total_products"], 2)
        self.assertEqual(summary["total_inventory_units"], 14)
        self.assertEqual(summary["total_inventory_asset_value"], 300.0)

    # ==========================================================================
    # 5. Complete Request Flow Integration Test
    # Flow: Product Added -> Inventory Updated -> Sale Created -> Revenue Updated
    # ==========================================================================

    def test_complete_business_flow(self) -> None:
        """
        Tests the end-to-end retail lifecycle requested by the user:
        Product Added -> Inventory Updated -> Sale Created -> Revenue Updated.
        """
        # Step 1: Product Added
        product = ProductService.add_product(
            name="Smart Fitness Tracker",
            price=120.0,
            category="Wearables",
            sku="FIT-9000",
            description="Waterproof heart-rate monitoring wristband",
            initial_stock=10,
            low_stock_threshold=5,
        )
        self.assertIsNotNone(product.id)
        self.assertEqual(product.price, 120.0)

        # Step 2: Inventory Updated (Restocked with 15 additional units)
        InventoryService.increase_stock(product_id=product.id, quantity=15)
        stock_status = InventoryService.check_stock(product.id)
        self.assertEqual(stock_status["quantity"], 25)  # 10 initial + 15 restocked = 25

        # Step 3: Sale Created (Customer buys 5 units with a 10% promotional discount)
        sale = SalesService.create_sale(
            product_id=product.id,
            quantity=5,
            discount=10.0,
        )
        # Expected: 5 units * $120 = $600 - 10% ($60) = $540
        self.assertEqual(sale.total_amount, 540.0)
        # Stock should now be decremented: 25 - 5 = 20 units
        stock_after_sale = InventoryService.check_stock(product.id)
        self.assertEqual(stock_after_sale["quantity"], 20)

        # Step 4: Revenue Updated
        rev = AnalyticsService.calculate_total_revenue()
        self.assertEqual(rev["total_revenue"], 540.0)
        self.assertEqual(rev["total_units_sold"], 5)
        self.assertEqual(rev["total_transactions"], 1)

        # Inventory Valuation Updated: 20 units remaining * $120 = $2,400.00
        inv_summary = AnalyticsService.get_inventory_summary()
        self.assertEqual(inv_summary["total_inventory_units"], 20)
        self.assertEqual(inv_summary["total_inventory_asset_value"], 2400.0)


if __name__ == "__main__":
    unittest.main()
