"""
Helper Functions and Custom Domain Exceptions Module.

Why this file exists:
1. Custom Exceptions:
   Instead of catching generic Python exceptions, production architectures define
   domain-specific exceptions (e.g. InsufficientStockError, ResourceNotFoundError).
   This allows routes and services to handle business edge cases cleanly and return
   appropriate HTTP status codes (404, 400, 409).

2. Uniform API Responses:
   Every API endpoint in a RESTful service should return a consistent JSON schema:
   {
       "success": true/false,
       "message": "Description of outcome",
       "data": { ... } or null
   }
   This consistency makes API integration predictable and effortless for any frontend or mobile client.
"""

from typing import Any, Tuple, Optional
from flask import jsonify, Response


# ==============================================================================
# Custom Domain Exception Classes (Object-Oriented Error Modeling)
# ==============================================================================


class BusinessLogicError(Exception):
    """Base class for all business logic and domain exceptions in this application."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ResourceNotFoundError(BusinessLogicError):
    """
    Raised when an entity (Product, Inventory, or Sale) cannot be found by its identifier.
    Maps naturally to HTTP 404 Not Found.
    """

    pass


class InsufficientStockError(BusinessLogicError):
    """
    Raised when an order or decrease request exceeds the currently available stock.
    Maps naturally to HTTP 400 Bad Request.
    """

    pass


class DuplicateResourceError(BusinessLogicError):
    """
    Raised when attempting to insert an entity with a unique field conflict (e.g. duplicate SKU).
    Maps naturally to HTTP 409 Conflict.
    """

    pass


class ValidationError(BusinessLogicError):
    """
    Raised when user input violates validation constraints.
    Maps naturally to HTTP 400 Bad Request.
    """

    pass


# ==============================================================================
# Standard API Response Formatters
# ==============================================================================


def format_response(
    success: bool = True,
    data: Any = None,
    message: str = "",
    status_code: int = 200,
) -> Tuple[Response, int]:
    """
    Creates a standardized, predictable JSON response tuple for Flask endpoints.

    Args:
        success (bool): True if the operation succeeded, False otherwise.
        data (Any, optional): The payload to return (dict, list, or primitive). Defaults to None.
        message (str, optional): A human-friendly message describing the outcome. Defaults to "".
        status_code (int, optional): HTTP status code (200, 201, etc.). Defaults to 200.

    Returns:
        Tuple[Response, int]: A Flask Response object containing JSON and the HTTP status code.
    """
    response_payload = {
        "success": success,
        "message": message,
        "data": data,
    }
    return jsonify(response_payload), status_code


def format_error(
    message: str,
    status_code: int = 400,
    details: Optional[Any] = None,
) -> Tuple[Response, int]:
    """
    Helper to construct an error JSON response.

    Args:
        message (str): Explanatory error message.
        status_code (int, optional): HTTP status code. Defaults to 400.
        details (Any, optional): Optional debugging details or field-level validation errors.

    Returns:
        Tuple[Response, int]: Flask JSON response tuple with error status code.
    """
    response_payload = {
        "success": False,
        "error": message,
        "details": details,
    }
    return jsonify(response_payload), status_code
