"""
Comprehensive Database Seeding Script.

Purpose:
Populates the SQLite database (`retail_stock.db`) with realistic retail data demonstrating
all five primary tables and their relationships:
1. `users`: System operators (managers, cashiers)
2. `suppliers`: Wholesale vendor partners
3. `products`: Catalog items linked to Users and Suppliers
4. `inventory`: Stock ledger records linked 1-to-1 with Products
5. `sales`: Retail customer purchases linked to Products
6. `purchase_orders`: Wholesale restock contracts linked to Products and Suppliers

Usage:
    python -m database.seed_data
"""

from datetime import datetime, timezone, timedelta
from app import create_app
from database.db import db
from models.user import User
from models.supplier import Supplier
from models.product import Product
from models.inventory import Inventory
from models.sales import Sale
from models.purchase_order import PurchaseOrder
from services.product_service import ProductService
from services.sales_service import SalesService
from services.supplier_service import SupplierService


def seed_database() -> None:
    """Populates all SQLite tables with connected sample data."""
    app = create_app("development")

    with app.app_context():
        print("--> Dropping existing tables and creating fresh SQLite schema...")
        db.drop_all()
        db.create_all()

        # ======================================================================
        # 1. Seed Users (User -> Creates Products)
        # ======================================================================
        print("--> 1. Seeding Users table...")
        admin_user = User(
            username="admin",
            email="admin@retailplatform.com",
            role="manager",
        )
        cashier_user = User(
            username="cashier1",
            email="cashier1@retailplatform.com",
            role="cashier",
        )
        db.session.add(admin_user)
        db.session.add(cashier_user)
        db.session.commit()
        print(f"    [+] Created User: {admin_user.username} (ID: {admin_user.id}, Role: {admin_user.role})")
        print(f"    [+] Created User: {cashier_user.username} (ID: {cashier_user.id}, Role: {cashier_user.role})")

        # ======================================================================
        # 2. Seed Suppliers (Supplier -> Supplies Many Products)
        # ======================================================================
        print("\n--> 2. Seeding Suppliers table...")
        supplier_data = [
            {
                "name": "Global Tech Wholesale Inc.",
                "contact_name": "Marcus Vance",
                "email": "orders@globaltech.com",
                "phone": "+1 (555) 234-5678",
                "category": "Electronics",
                "address": "450 Industrial Parkway, San Jose, CA",
                "rating": 4.8,
            },
            {
                "name": "Apex Ergonomics & Furniture Co.",
                "contact_name": "Elena Rostova",
                "email": "sales@apexcomfort.com",
                "phone": "+1 (555) 876-5432",
                "category": "Furniture",
                "address": "820 Commerce Blvd, Grand Rapids, MI",
                "rating": 4.6,
            },
            {
                "name": "OmniConnect Digital Supplies",
                "contact_name": "David Chen",
                "email": "supply@omniconnect.net",
                "phone": "+1 (555) 345-6789",
                "category": "Accessories",
                "address": "1200 Logistics Way, Dallas, TX",
                "rating": 4.9,
            },
        ]
        created_suppliers: list[Supplier] = []
        for s_info in supplier_data:
            s_obj = SupplierService.add_supplier(**s_info)
            created_suppliers.append(s_obj)
            print(f"    [+] Created Supplier: {s_obj.name} (ID: {s_obj.id}, Category: {s_obj.category})")

        # Map categories to supplier IDs
        supplier_map = {
            "Electronics": created_suppliers[0].id,
            "Furniture": created_suppliers[1].id,
            "Accessories": created_suppliers[2].id,
        }

        # ======================================================================
        # 3. Seed Products (Connected to User and Supplier)
        # ======================================================================
        print("\n--> 3. Seeding Products & Inventory tables...")
        sample_products = [
            {
                "sku": "TECH-1001",
                "name": "Logitech MX Master 3S Wireless Mouse",
                "category": "Electronics",
                "price": 99.99,
                "description": "Ergonomic high-precision wireless mouse with MagSpeed scroll.",
                "initial_stock": 45,
                "low_stock_threshold": 10,
            },
            {
                "sku": "TECH-1002",
                "name": "Keychron K2 Mechanical Keyboard",
                "category": "Electronics",
                "price": 89.99,
                "description": "Wireless Bluetooth mechanical keyboard with Gateron Brown switches.",
                "initial_stock": 28,
                "low_stock_threshold": 8,
            },
            {
                "sku": "TECH-1003",
                "name": "Dell UltraSharp 27-inch 4K Monitor",
                "category": "Electronics",
                "price": 449.99,
                "description": "IPS panel with 99% sRGB color gamut and USB-C power delivery.",
                "initial_stock": 8,  # Intentionally low to trigger alert
                "low_stock_threshold": 10,
            },
            {
                "sku": "FURN-2001",
                "name": "Ergonomic Mesh Office Chair",
                "category": "Furniture",
                "price": 199.50,
                "description": "Breathable mesh back with adjustable lumbar support and 3D armrests.",
                "initial_stock": 14,
                "low_stock_threshold": 5,
            },
            {
                "sku": "FURN-2002",
                "name": "Motorized Standing Desk (55x28 in)",
                "category": "Furniture",
                "price": 329.00,
                "description": "Dual-motor electric height-adjustable desk with memory presets.",
                "initial_stock": 4,  # Intentionally low
                "low_stock_threshold": 5,
            },
            {
                "sku": "ACCS-3001",
                "name": "Anker 100W USB-C Fast Charger",
                "category": "Accessories",
                "price": 49.99,
                "description": "GaN III 3-port compact fast wall charger.",
                "initial_stock": 60,
                "low_stock_threshold": 15,
            },
        ]

        created_products: list[Product] = []
        for p in sample_products:
            assigned_sup_id = supplier_map.get(p["category"], created_suppliers[0].id)
            prod = ProductService.add_product(
                sku=p["sku"],
                name=p["name"],
                category=p["category"],
                price=p["price"],
                description=p["description"],
                initial_stock=p["initial_stock"],
                low_stock_threshold=p["low_stock_threshold"],
                created_by_user_id=admin_user.id,
                supplier_id=assigned_sup_id,
            )
            created_products.append(prod)
            print(f"    [+] Created Product: {prod.name} (SKU: {prod.sku}) -> Supplier: #{assigned_sup_id}, User: #{admin_user.id}")

        # ======================================================================
        # 4. Seed Sales (Product -> Has Many Sales)
        # ======================================================================
        print("\n--> 4. Seeding Sales table (Product -> Has Many Sales)...")
        sales_to_simulate = [
            {"product_index": 0, "quantity": 3, "discount": 0.0},
            {"product_index": 0, "quantity": 2, "discount": 10.0},
            {"product_index": 1, "quantity": 4, "discount": 5.0},
            {"product_index": 2, "quantity": 1, "discount": 0.0},
            {"product_index": 3, "quantity": 2, "discount": 15.0},
            {"product_index": 5, "quantity": 8, "discount": 0.0},
        ]

        for s in sales_to_simulate:
            target_prod = created_products[s["product_index"]]
            sale = SalesService.create_sale(
                product_id=target_prod.id,
                quantity=s["quantity"],
                discount=s["discount"],
            )
            print(
                f"    [$] Sale TX-{sale.id:04d}: {sale.quantity}x {target_prod.name} "
                f"| Revenue: ${sale.total_amount:.2f} (Stock remaining: {target_prod.inventory.quantity})"
            )

        # ======================================================================
        # 5. Seed Purchase Orders (Product -> Can Have Many Purchase Orders)
        # ======================================================================
        print("\n--> 5. Seeding Purchase Orders table (Product -> Has Many Purchase Orders)...")
        purchase_orders_to_create = [
            {
                "order_number": "PO-2026-001",
                "product_id": created_products[2].id,  # Dell 4K Monitor (Low Stock)
                "supplier_id": supplier_map["Electronics"],
                "quantity": 15,
                "unit_cost": 310.00,
                "status": "PENDING",
            },
            {
                "order_number": "PO-2026-002",
                "product_id": created_products[4].id,  # Standing Desk (Low Stock)
                "supplier_id": supplier_map["Furniture"],
                "quantity": 10,
                "unit_cost": 210.00,
                "status": "RECEIVED",
                "delivery_date": datetime.now(timezone.utc) - timedelta(days=2),
            },
            {
                "order_number": "PO-2026-003",
                "product_id": created_products[0].id,  # MX Master 3S
                "supplier_id": supplier_map["Electronics"],
                "quantity": 25,
                "unit_cost": 65.00,
                "status": "PENDING",
            },
        ]

        for po_data in purchase_orders_to_create:
            po = PurchaseOrder(**po_data)
            db.session.add(po)
            db.session.commit()
            print(f"    [#] Purchase Order {po.order_number}: {po.quantity}x {po.product.name} from {po.supplier.name} | Total Cost: ${po.total_cost:.2f} [Status: {po.status}]")

        print("\n=======================================================")
        print(" SQLite Database successfully seeded with all 5 tables!")
        print(" Users, Suppliers, Products, Sales, Purchase Orders")
        print("=======================================================\n")


if __name__ == "__main__":
    seed_database()
