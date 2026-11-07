# Retail Stock Optimization and Sales Intelligence Platform

A modular, service-based Flask backend business logic layer engineered for retail stock management, transaction processing, inventory optimization, and sales intelligence.

---

## 🏛️ Architecture Overview

The system uses a **Service-Based 3-Tier Backend Architecture**:

```
+-------------------------------------------------------------+
|                     Client / API Caller                     |
|                 (Postman / cURL / Frontend)                 |
+-------------------------------------------------------------+
                              │
                              ▼  (HTTP REST JSON Requests)
+─────────────────────────────────────────────────────────────+
|               Flask Route Layer (Controllers)               |
|   product_routes.py | inventory_routes.py | sales_routes.py  |
+─────────────────────────────────────────────────────────────+
                              │
                              ▼  (Validated Python Method Calls)
+─────────────────────────────────────────────────────────────+
|                     Business Logic Layer                    |
|   ProductService    | InventoryService    | SalesService    |
|                     | AnalyticsService    |                 |
+─────────────────────────────────────────────────────────────+
                              │
                              ▼  (SQLAlchemy ORM Model Entities)
+─────────────────────────────────────────────────────────────+
|                      Persistence Layer                      |
|           Product     |     Inventory     |     Sale        |
+─────────────────────────────────────────────────────────────+
                              │
                              ▼  (SQL Queries)
+─────────────────────────────────────────────────────────────+
|                       SQLite Database                       |
|                      (retail_stock.db)                      |
+─────────────────────────────────────────────────────────────+
```

---

## 📁 Directory Structure

```text
inventory-management-system/
├── app.py                     # Flask application factory (create_app) & server runner
├── requirements.txt           # Project dependencies (Flask, Flask-SQLAlchemy)
├── retail_stock.db            # SQLite database file (generated automatically)
│
├── config/
│   ├── __init__.py
│   └── config.py              # Configuration classes (Development, Testing)
│
├── database/
│   ├── __init__.py
│   ├── db.py                  # SQLAlchemy db instance & init_db table creator
│   └── seed_data.py           # Demo seeder for Viva demonstrations
│
├── models/
│   ├── __init__.py
│   ├── product.py             # Product entity (SKU, title, category, price)
│   ├── inventory.py           # Inventory entity (stock count, alerts, timestamps)
│   └── sales.py               # Sale transaction entity (historical unit price, discounts)
│
├── services/
│   ├── __init__.py
│   ├── product_service.py     # Product CRUD & search logic
│   ├── inventory_service.py   # Restocking, deductions, low-stock threshold queries
│   ├── sales_service.py       # POS calculation, stock deduction, sale recording
│   └── analytics_service.py   # Revenue, best-sellers, inventory valuation analytics
│
├── routes/
│   ├── __init__.py
│   ├── product_routes.py      # /api/products endpoints
│   ├── inventory_routes.py    # /api/inventory endpoints
│   ├── sales_routes.py        # /api/sales endpoints
│   └── analytics_routes.py    # /api/analytics endpoints
│
├── utils/
│   ├── __init__.py
│   ├── validators.py          # Input format and boundary validation
│   └── helpers.py             # Custom domain exceptions & JSON response formatters
│
└── tests/
    ├── test_services.py       # Unit tests for core service business logic
    └── test_routes.py         # HTTP integration tests via Flask test client
```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed Demo Data (Optional for testing)
```bash
python -m database.seed_data
```

### 3. Run the Backend Server
```bash
python app.py
```
Server runs at: `http://127.0.0.1:5000`

### 4. Run Automated Test Suite
```bash
python -m unittest discover tests
```

---

## 🔄 End-to-End Request Flow

The core lifecycle of a retail item through the system:

```text
1. Product Added
   POST /api/products
   └─ ProductService.add_product()
      ├─ Validates SKU uniqueness & price > 0
      ├─ Creates Product row
      └─ Initializes linked Inventory row (stock = 10)

2. Inventory Updated
   POST /api/inventory/1/increase
   └─ InventoryService.increase_stock(product_id=1, quantity=15)
      ├─ Validates quantity > 0
      ├─ Increments stock: 10 + 15 = 25 units
      └─ Records last_restocked_at timestamp

3. Sale Created
   POST /api/sales
   └─ SalesService.create_sale(product_id=1, quantity=5, discount=10%)
      ├─ Fetches current price ($120.00)
      ├─ Calculates total: 5 * $120 = $600 - 10% ($60) = $540.00
      ├─ Calls InventoryService.decrease_stock(product_id=1, quantity=5)
      │  └─ Stock drops from 25 -> 20 units
      └─ Persists immutable Sale record

4. Revenue & Inventory Intelligence Updated
   GET /api/analytics/revenue
   GET /api/analytics/inventory-summary
   └─ AnalyticsService
      ├─ Total Revenue increases by +$540.00
      ├─ Top-Selling rankings update with sold units
      └─ Inventory asset valuation recalculates (20 remaining * $120 = $2,400)
```

---

## 🎯 Viva Q&A / Architecture Highlights

1. **Why separate routes from services?**
   - Routes only understand HTTP (JSON, status codes, query parameters).
   - Services contain pure business logic (pricing, inventory deductions, validations).
   - This allows reusing the same service methods across REST APIs, CLI commands, or background Celery tasks.

2. **Why does Sale store `unit_price` separately from `Product.price`?**
   - If a store updates a product price tomorrow from \$100 to \$150, past sales must continue to show \$100 for financial auditing and tax accuracy.

3. **How is negative stock prevented?**
   - `InventoryService.decrease_stock()` checks `if inventory.quantity < quantity:` before deducting, throwing an `InsufficientStockError` and rolling back the database transaction.
