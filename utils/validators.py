"""
Validation Utilities Module.

Why this file exists:
Input validation is the first line of defense in backend systems.
Never trust client input! Before processing data in our business logic layer (services),
we validate types, presence of required keys, numeric boundaries, and string formats.
Raising explicit ValueErrors allows services and routes to return helpful 400 Bad Request messages.
"""

from typing import Dict, Any


def validate_positive_number(value: Any, field_name: str) -> float:
    """
    Validates that a given value can be converted to a positive float (> 0).

    Args:
        value (Any): The input value to check.
        field_name (str): The name of the field for descriptive error messaging.

    Returns:
        float: The validated positive float.

    Raises:
        ValueError: If the value is missing, non-numeric, or <= 0.
    """
    if value is None:
        raise ValueError(f"Field '{field_name}' is required.")

    try:
        numeric_val = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"Field '{field_name}' must be a valid numeric number.")

    if numeric_val <= 0:
        raise ValueError(f"Field '{field_name}' must be strictly greater than 0.")

    return numeric_val


def validate_positive_integer(value: Any, field_name: str) -> int:
    """
    Validates that a given value is a non-negative integer (>= 0).

    Args:
        value (Any): The input value to check.
        field_name (str): The name of the field for descriptive error messaging.

    Returns:
        int: The validated positive integer.

    Raises:
        ValueError: If the value is missing, not an integer, or < 0.
    """
    if value is None:
        raise ValueError(f"Field '{field_name}' is required.")

    try:
        int_val = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"Field '{field_name}' must be an integer.")

    if int_val < 0:
        raise ValueError(f"Field '{field_name}' cannot be negative.")

    return int_val


def validate_product_payload(data: Dict[str, Any]) -> None:
    """
    Validates the dictionary payload sent when creating or updating a Product.

    Checks:
    1. Payload must be a dictionary.
    2. 'name', 'category', 'sku', and 'price' must be provided.
    3. Strings must not be blank.
    4. Price must be > 0.

    Args:
        data (Dict[str, Any]): Client JSON request dictionary.

    Raises:
        ValueError: If any validation rule fails.
    """
    if not isinstance(data, dict):
        raise ValueError("Invalid request format. Expected a JSON object.")

    # List of mandatory fields needed to create a new Product
    required_fields = ["name", "category", "sku", "price"]
    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValueError(f"Missing required field: '{field}'")

    # Validate non-empty string fields
    for str_field in ["name", "category", "sku"]:
        val = str(data.get(str_field, "")).strip()
        if not val:
            raise ValueError(f"Field '{str_field}' cannot be empty or whitespace.")

    # Validate price is a positive number
    validate_positive_number(data.get("price"), "price")

    # Validate optional initial stock if provided
    if "initial_stock" in data:
        validate_positive_integer(data.get("initial_stock"), "initial_stock")

    # Validate optional low stock threshold if provided
    if "low_stock_threshold" in data:
        validate_positive_integer(
            data.get("low_stock_threshold"), "low_stock_threshold"
        )


def validate_inventory_adjustment(quantity: Any) -> int:
    """
    Validates quantity passed to stock adjustment endpoints (must be an integer > 0).

    Args:
        quantity (Any): Units to increase or decrease.

    Returns:
        int: Validated positive integer.

    Raises:
        ValueError: If quantity <= 0.
    """
    val = validate_positive_integer(quantity, "quantity")
    if val <= 0:
        raise ValueError("Stock adjustment quantity must be strictly greater than 0.")
    return val


def validate_sale_payload(data: Dict[str, Any]) -> None:
    """
    Validates the dictionary payload sent when recording a new Sale.

    Checks:
    1. 'product_id' is provided and is a positive integer.
    2. 'quantity' is provided and is >= 1.
    3. 'discount' (if provided) is between 0% and 100%.

    Args:
        data (Dict[str, Any]): Client JSON request dictionary.

    Raises:
        ValueError: If any validation rule fails.
    """
    if not isinstance(data, dict):
        raise ValueError("Invalid request format. Expected a JSON object.")

    if "product_id" not in data or data["product_id"] is None:
        raise ValueError("Missing required field: 'product_id'")
    validate_positive_integer(data.get("product_id"), "product_id")

    if "quantity" not in data or data["quantity"] is None:
        raise ValueError("Missing required field: 'quantity'")
    qty = validate_positive_integer(data.get("quantity"), "quantity")
    if qty <= 0:
        raise ValueError("Sale quantity must be at least 1 unit.")

    if "discount" in data and data["discount"] is not None:
        try:
            discount = float(data["discount"])
        except (ValueError, TypeError):
            raise ValueError("Field 'discount' must be a valid number.")

        if discount < 0 or discount > 100:
            raise ValueError(
                "Discount percentage must be between 0 and 100 (e.g., 10 for 10% off)."
            )
