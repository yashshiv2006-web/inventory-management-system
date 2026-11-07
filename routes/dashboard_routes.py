"""
Frontend Web Routes & View Controller Module.

Why this file exists:
In Full-Stack Flask applications, Web Routes (or View Controllers) serve HTML templates
rendered using Jinja2 template inheritance. They:
1. Handle browser navigation (GET /dashboard, GET /products, etc.).
2. Fetch data from Service classes to pre-populate templates on the server side.
3. Process standard HTML form submissions (POST /products/add, POST /sales/create) with flash messaging.
4. Provide seamless fallback and compatibility with client-side JavaScript (Fetch / AJAX).
"""

from typing import Any
import csv
import io
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    Response,
    jsonify,
    session,
)
from services.product_service import ProductService
from services.inventory_service import InventoryService
from services.sales_service import SalesService
from services.analytics_service import AnalyticsService
from services.supplier_service import SupplierService
from services.forcasting_services import ForecastingService
from utils.helpers import (
    ResourceNotFoundError,
    InsufficientStockError,
    DuplicateResourceError,
    ValidationError,
)

# Create Blueprint for all web views
web_bp = Blueprint("web_bp", __name__)


# ==============================================================================
# Authentication & Demo Session Routes
# ==============================================================================

@web_bp.route("/login", methods=["GET", "POST"])
def login() -> Any:
    """
    Renders login screen and handles simple educational authentication.
    Credentials for demo: admin / admin123
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Educational hardcoded demo check
        if username == "admin" and password == "admin123":
            session["logged_in"] = True
            session["username"] = "Store Manager"
            flash("Welcome back, Store Manager!", "success")
            return redirect(url_for("web_bp.dashboard"))
        else:
            flash("Invalid credentials! Use demo login: admin / admin123", "danger")

    return render_template("login.html")


@web_bp.route("/logout", methods=["GET"])
def logout() -> Any:
    """Clears user session and redirects to login."""
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("web_bp.login"))


# ==============================================================================
# Dashboard View
# ==============================================================================

@web_bp.route("/", methods=["GET"])
@web_bp.route("/dashboard", methods=["GET"])
def dashboard() -> Any:
    """
    Renders the modern Executive Dashboard with KPI cards, overview charts,
    recent sales, and urgent low-stock warnings.
    """
    revenue_metrics = AnalyticsService.calculate_total_revenue()
    inventory_summary = AnalyticsService.get_inventory_summary()
    top_sellers = AnalyticsService.get_top_selling_products(limit=5)
    low_stock_items = InventoryService.get_low_stock_products()
    recent_sales = SalesService.get_sales_history()[:6]
    forecast_metrics = ForecastingService.get_summary_metrics()

    top_product_name = top_sellers[0]["product_name"] if top_sellers else "N/A"

    return render_template(
        "dashboard.html",
        revenue_metrics=revenue_metrics,
        inventory_summary=inventory_summary,
        top_sellers=top_sellers,
        low_stock_items=low_stock_items,
        recent_sales=recent_sales,
        forecast_metrics=forecast_metrics,
        top_product_name=top_product_name,
        active_page="dashboard",
    )


# ==============================================================================
# Products Views & Actions (Add, Edit, Delete, Search)
# ==============================================================================

@web_bp.route("/products", methods=["GET"])
def products() -> Any:
    """Renders catalog table with optional search query filtering."""
    query = request.args.get("q", "").strip()
    if query:
        product_list = ProductService.search_product(query)
    else:
        product_list = ProductService.list_products()

    return render_template(
        "products.html",
        products=product_list,
        search_query=query,
        active_page="products",
    )


@web_bp.route("/products/add", methods=["GET", "POST"])
def add_product() -> Any:
    """Renders add product form and processes submission."""
    suppliers = SupplierService.list_suppliers()

    if request.method == "POST":
        try:
            sku = request.form.get("sku", "").strip()
            name = request.form.get("name", "").strip()
            category = request.form.get("category", "").strip()
            price = float(request.form.get("price", 0))
            description = request.form.get("description", "").strip()
            initial_stock = int(request.form.get("initial_stock", 0))
            low_stock_threshold = int(request.form.get("low_stock_threshold", 10))
            sup_id_raw = request.form.get("supplier_id")
            supplier_id = int(sup_id_raw) if sup_id_raw and sup_id_raw.isdigit() else None

            ProductService.add_product(
                sku=sku,
                name=name,
                category=category,
                price=price,
                description=description,
                initial_stock=initial_stock,
                low_stock_threshold=low_stock_threshold,
                supplier_id=supplier_id,
            )
            flash(f"Product '{name}' added successfully to catalog!", "success")
            return redirect(url_for("web_bp.products"))

        except (ValidationError, DuplicateResourceError, ValueError) as err:
            flash(str(err), "danger")
        except Exception as err:
            flash(f"Unexpected error: {str(err)}", "danger")

    return render_template("add_product.html", suppliers=suppliers, active_page="products")


@web_bp.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id: int) -> Any:
    """Renders edit product form pre-filled and updates fields."""
    suppliers = SupplierService.list_suppliers()
    try:
        product = ProductService.get_product_by_id(product_id)
    except ResourceNotFoundError:
        flash(f"Product #{product_id} not found.", "warning")
        return redirect(url_for("web_bp.products"))

    if request.method == "POST":
        try:
            sku = request.form.get("sku", "").strip()
            name = request.form.get("name", "").strip()
            category = request.form.get("category", "").strip()
            price = float(request.form.get("price", 0))
            description = request.form.get("description", "").strip()
            sup_id_raw = request.form.get("supplier_id")
            supplier_id = int(sup_id_raw) if sup_id_raw and sup_id_raw.isdigit() else None

            ProductService.update_product(
                product_id=product_id,
                sku=sku,
                name=name,
                category=category,
                price=price,
                description=description,
                supplier_id=supplier_id,
            )
            flash(f"Product '{name}' updated successfully!", "success")
            return redirect(url_for("web_bp.products"))

        except (ValidationError, DuplicateResourceError, ValueError) as err:
            flash(str(err), "danger")

    return render_template(
        "edit_product.html", product=product, suppliers=suppliers, active_page="products"
    )


@web_bp.route("/products/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id: int) -> Any:
    """Deletes a product through web form submission."""
    try:
        ProductService.delete_product(product_id)
        flash("Product deleted successfully.", "info")
    except Exception as err:
        flash(f"Could not delete product: {str(err)}", "danger")

    return redirect(url_for("web_bp.products"))


# ==============================================================================
# Inventory Management & Restocking Views
# ==============================================================================

@web_bp.route("/inventory", methods=["GET"])
def inventory() -> Any:
    """Renders inventory status table, low stock alerts, and quick restock actions."""
    products = ProductService.list_products()
    low_stock_items = InventoryService.get_low_stock_products()
    suppliers = SupplierService.list_suppliers()

    return render_template(
        "inventory.html",
        products=products,
        low_stock_items=low_stock_items,
        suppliers=suppliers,
        active_page="inventory",
    )


@web_bp.route("/inventory/adjust", methods=["POST"])
def adjust_inventory() -> Any:
    """Handles stock replenishment or manual deductions from UI."""
    try:
        product_id = int(request.form.get("product_id", 0))
        quantity = int(request.form.get("quantity", 0))
        action = request.form.get("action", "increase")

        if action == "increase":
            InventoryService.increase_stock(product_id, quantity)
            flash(f"Restocked {quantity} units successfully!", "success")
        elif action == "decrease":
            InventoryService.decrease_stock(product_id, quantity)
            flash(f"Deducted {quantity} units from inventory.", "warning")

    except InsufficientStockError as err:
        flash(str(err), "danger")
    except Exception as err:
        flash(f"Inventory error: {str(err)}", "danger")

    return redirect(url_for("web_bp.inventory"))


# ==============================================================================
# Point-of-Sale & Sales History Views
# ==============================================================================

@web_bp.route("/sales", methods=["GET"])
def sales() -> Any:
    """Renders point-of-sale interface and historical transaction table."""
    products = ProductService.list_products()
    sales_history = SalesService.get_sales_history()
    revenue_metrics = AnalyticsService.calculate_total_revenue()

    return render_template(
        "sales.html",
        products=products,
        sales=sales_history,
        revenue=revenue_metrics,
        active_page="sales",
    )


@web_bp.route("/sales/create", methods=["POST"])
def create_sale_web() -> Any:
    """Processes point-of-sale form submission."""
    try:
        product_id = int(request.form.get("product_id", 0))
        quantity = int(request.form.get("quantity", 0))
        discount = float(request.form.get("discount", 0.0))

        sale = SalesService.create_sale(
            product_id=product_id, quantity=quantity, discount=discount
        )
        flash(
            f"Sale #{sale.id} completed! Total: ${sale.total_amount:.2f} ({quantity} units sold)",
            "success",
        )
    except InsufficientStockError as err:
        flash(f"Stock Error: {str(err)}", "danger")
    except Exception as err:
        flash(f"Sale Failed: {str(err)}", "danger")

    return redirect(url_for("web_bp.sales"))


# ==============================================================================
# Analytics & Reports Views
# ==============================================================================

@web_bp.route("/analytics", methods=["GET"])
def analytics() -> Any:
    """Renders comprehensive charts, sales velocity, and executive KPIs."""
    revenue_metrics = AnalyticsService.calculate_total_revenue()
    inventory_summary = AnalyticsService.get_inventory_summary()
    top_sellers = AnalyticsService.get_top_selling_products(limit=10)
    low_stock_items = InventoryService.get_low_stock_products()

    return render_template(
        "analytics.html",
        revenue_metrics=revenue_metrics,
        inventory_summary=inventory_summary,
        top_sellers=top_sellers,
        low_stock_items=low_stock_items,
        active_page="analytics",
    )


@web_bp.route("/reports", methods=["GET"])
def reports() -> Any:
    """
    Renders the Reports center and supports live CSV export of audit tables.
    """
    export_format = request.args.get("format")
    report_type = request.args.get("type", "inventory")

    # Handle CSV Export if requested
    if export_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)

        if report_type == "inventory":
            writer.writerow(["ID", "SKU", "Product Name", "Category", "Price", "Current Stock", "Threshold", "Status"])
            products = ProductService.list_products()
            for p in products:
                stock = p.inventory.quantity if p.inventory else 0
                threshold = p.inventory.low_stock_threshold if p.inventory else 10
                status = p.inventory.get_stock_status() if p.inventory else "UNKNOWN"
                writer.writerow([p.id, p.sku, p.name, p.category, f"{p.price:.2f}", stock, threshold, status])

            filename = "inventory_valuation_report.csv"

        elif report_type == "sales":
            writer.writerow(["Transaction ID", "Product", "SKU", "Quantity", "Unit Price", "Discount %", "Total Revenue", "Date"])
            sales = SalesService.get_sales_history()
            for s in sales:
                p_name = s.product.name if s.product else "N/A"
                p_sku = s.product.sku if s.product else "N/A"
                writer.writerow([s.id, p_name, p_sku, s.quantity, f"{s.unit_price:.2f}", f"{s.discount:.1f}", f"{s.total_amount:.2f}", s.sale_date.strftime("%Y-%m-%d %H:%M")])

            filename = "sales_audit_report.csv"

        else:
            filename = "retail_report.csv"

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"},
        )

    # Standard HTML page render
    products = ProductService.list_products()
    sales = SalesService.get_sales_history()
    suppliers = SupplierService.list_suppliers()
    inventory_summary = AnalyticsService.get_inventory_summary()
    revenue_metrics = AnalyticsService.calculate_total_revenue()

    return render_template(
        "reports.html",
        products=products,
        sales=sales,
        suppliers=suppliers,
        inventory_summary=inventory_summary,
        revenue_metrics=revenue_metrics,
        active_page="reports",
    )


# ==============================================================================
# Demand Forecasting View
# ==============================================================================

@web_bp.route("/forecasting", methods=["GET"])
def forecasting() -> Any:
    """Renders AI/Statistical demand prediction & reorder recommendations."""
    forecasts = ForecastingService.predict_demand(forecast_days=30)
    summary_metrics = ForecastingService.get_summary_metrics()

    return render_template(
        "forecasting.html",
        forecasts=forecasts,
        summary=summary_metrics,
        active_page="forecasting",
    )


# ==============================================================================
# Supplier API Endpoint
# ==============================================================================

@web_bp.route("/api/suppliers", methods=["GET"])
def get_suppliers_api() -> Any:
    """API endpoint providing supplier directory for client-side JavaScript."""
    suppliers = SupplierService.list_suppliers()
    return jsonify({
        "success": True,
        "data": [s.to_dict() for s in suppliers],
        "message": f"Retrieved {len(suppliers)} suppliers.",
    })
