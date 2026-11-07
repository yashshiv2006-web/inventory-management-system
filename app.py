"""
Flask Application Factory and Server Entry Point.

Project: Retail Stock Optimization and Sales Intelligence Platform
Architecture: Service-Based Architecture with Flask Blueprints and SQLAlchemy ORM.

Why this file exists:
In modern Flask development, the "Application Factory Pattern" (`create_app`) is standard.
Instead of creating a global application instance, a factory function creates and configures
the app at runtime. This allows:
1. Painless switching between configurations (Development, Testing, Production).
2. Clean integration with automated unit tests.
3. Modular registration of domain Blueprints (Products, Inventory, Sales, Analytics).
"""

import os
from typing import Tuple, Dict, Any
from flask import Flask, jsonify, Response
from config.config import config_by_name
from database.db import init_db
from routes.product_routes import product_bp
from routes.inventory_routes import inventory_bp
from routes.sales_routes import sales_bp
from routes.analytics_routes import analytics_bp
from routes.dashboard_routes import web_bp
from routes.auth_routes import auth_bp
from routes.reports_routes import reports_bp


def create_app(config_name: str | None = None) -> Flask:
    """
    Application factory function that initializes and configures the Flask application.

    Args:
        config_name (str, optional): Configuration environment ('development', 'production', 'testing').
                                    Defaults to 'production' on Vercel, else 'development'.

    Returns:
        Flask: The configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get(
            "FLASK_ENV", "production" if os.environ.get("VERCEL") else "development"
        )

    base_dir = os.path.abspath(os.path.dirname(__file__))

    # 1. Instantiate the core Flask application with explicit absolute paths for templates & static
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static"),
    )

    # 2. Load environment-specific configurations
    selected_config = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(selected_config)

    # 3. Initialize the database and create SQLite tables
    init_db(app)

    # 4. Register REST API and Web Blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(analytics_bp)

    # 5. Global Error Handlers (Return structured JSON instead of default HTML error pages)
    @app.errorhandler(404)
    def handle_not_found(error: Any) -> Tuple[Response, int]:
        """Custom handler for non-existent routes."""
        return jsonify({
            "success": False,
            "error": "The requested API endpoint was not found.",
            "status_code": 404,
        }), 404

    @app.errorhandler(400)
    def handle_bad_request(error: Any) -> Tuple[Response, int]:
        """Custom handler for bad request errors."""
        return jsonify({
            "success": False,
            "error": "Bad request syntax or malformed parameters.",
            "status_code": 400,
        }), 400

    @app.errorhandler(500)
    def handle_internal_error(error: Any) -> Tuple[Response, int]:
        """Custom handler for unhandled server exceptions."""
        return jsonify({
            "success": False,
            "error": "An internal server error occurred while processing the request.",
            "status_code": 500,
        }), 500

    # 6. Service Health Check & API Directory Route
    @app.route("/", methods=["GET"])
    @app.route("/api/health", methods=["GET"])
    def health_check() -> Tuple[Response, int]:
        """
        API Health Check and Root Directory.
        Provides a friendly overview of available REST endpoints.
        """
        return jsonify({
            "status": "healthy",
            "project": "Retail Stock Optimization and Sales Intelligence Platform",
            "version": "1.0.0",
            "architecture": "Service-Based Flask Architecture (OOP)",
            "database": "SQLite (via SQLAlchemy ORM)",
            "endpoints": {
                "products": [
                    "POST   /api/products           (Add new product)",
                    "GET    /api/products           (List all products)",
                    "GET    /api/products/<id>     (Get product details)",
                    "PUT    /api/products/<id>     (Update product)",
                    "DELETE /api/products/<id>     (Delete product)",
                    "GET    /api/products/search?q (Search by name/category/sku)",
                ],
                "inventory": [
                    "GET    /api/inventory/<id>          (Check stock status)",
                    "POST   /api/inventory/<id>/increase (Restock quantity)",
                    "POST   /api/inventory/<id>/decrease (Manual stock deduction)",
                    "GET    /api/inventory/low-stock     (Low stock alerts)",
                ],
                "sales": [
                    "POST   /api/sales               (Record a new sale)",
                    "GET    /api/sales?product_id=   (Retrieve sales history)",
                ],
                "analytics": [
                    "GET    /api/analytics/revenue            (Total revenue & AOV)",
                    "GET    /api/analytics/top-selling?limit= (Best sellers ranking)",
                    "GET    /api/analytics/inventory-summary  (Stock valuation & KPIs)",
                ],
            },
        }), 200

    return app


# Create the application instance for WSGI servers (like Gunicorn/Vercel) and direct execution
app = create_app()

if __name__ == "__main__":
    # In development mode, Flask provides an interactive debugger and reloader
    print("\n" + "=" * 65)
    print(" Retail Stock Optimization and Sales Intelligence Platform")
    print(" Flask Backend Server running at: http://127.0.0.1:5000")
    print("=" * 65 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=True)