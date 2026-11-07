"""
Database Connection & Initialization Module.

Purpose:
Configures SQLAlchemy ORM, enables SQLite foreign key constraint enforcement,
prevents circular imports, and manages automated table creation.

Why this file exists:
1. Prevents Circular Imports:
   Models and the Flask app factory both import `db` from this centralized module.
2. Enforces SQLite Foreign Keys:
   By default, SQLite disables foreign key constraints. We attach an event listener
   to SQLite database connections to execute 'PRAGMA foreign_keys=ON', ensuring
   referential integrity (e.g. cascading deletes) is strictly enforced.
3. Automated Schema Creation:
   `init_db(app)` discovers all registered SQLAlchemy models and automatically executes
   CREATE TABLE IF NOT EXISTS statements upon application startup.
"""

from typing import Any
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy.engine import Engine
from sqlalchemy import event

# Instantiate the SQLAlchemy ORM instance
db: SQLAlchemy = SQLAlchemy()


# ==============================================================================
# SQLite Foreign Key Enforcement Event Listener
# ==============================================================================

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    """
    Enforces foreign key constraint checks on SQLite databases.
    Without this PRAGMA, SQLite silently ignores FOREIGN KEY references.
    """
    # Check if the underlying database driver is SQLite
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    except Exception:
        pass


# ==============================================================================
# Database Initialization Function
# ==============================================================================

def init_db(app: Flask) -> None:
    """
    Binds SQLAlchemy to the Flask app and creates all database tables.

    Args:
        app (Flask): Active Flask application instance.
    """
    # 1. Bind SQLAlchemy to the Flask app instance
    db.init_app(app)

    # 2. Within the app context, import models so metadata is registered, then create tables
    with app.app_context():
        # Import all models to ensure SQLAlchemy is aware of their table schemas
        from models.user import User
        from models.supplier import Supplier
        from models.product import Product
        from models.inventory import Inventory
        from models.sales import Sale
        from models.purchase_order import PurchaseOrder

        # Executes CREATE TABLE IF NOT EXISTS for all defined models
        db.create_all()
