"""
Utils package initialization.
Exports validation utilities, response formatters, and domain exceptions.
"""

from .validators import (
    validate_product_payload,
    validate_inventory_adjustment,
    validate_sale_payload,
    validate_positive_number,
    validate_positive_integer,
)
from .helpers import (
    format_response,
    format_error,
    BusinessLogicError,
    ResourceNotFoundError,
    InsufficientStockError,
    DuplicateResourceError,
    ValidationError,
)

__all__ = [
    "validate_product_payload",
    "validate_inventory_adjustment",
    "validate_sale_payload",
    "validate_positive_number",
    "validate_positive_integer",
    "format_response",
    "format_error",
    "BusinessLogicError",
    "ResourceNotFoundError",
    "InsufficientStockError",
    "DuplicateResourceError",
    "ValidationError",
]
