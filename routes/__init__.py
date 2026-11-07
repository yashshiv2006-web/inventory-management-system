"""
Routes package initialization.
Exports all API and Web Blueprints:
- product_bp
- inventory_bp
- sales_bp
- analytics_bp
- web_bp
- auth_bp
- reports_bp
"""

from .product_routes import product_bp
from .inventory_routes import inventory_bp
from .sales_routes import sales_bp
from .analytics_routes import analytics_bp
from .dashboard_routes import web_bp
from .auth_routes import auth_bp
from .reports_routes import reports_bp

__all__ = [
    "product_bp",
    "inventory_bp",
    "sales_bp",
    "analytics_bp",
    "web_bp",
    "auth_bp",
    "reports_bp",
]
