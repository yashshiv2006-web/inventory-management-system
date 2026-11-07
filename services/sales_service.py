"""
Sales Service Module.

Why this file exists:
In a retail business, making a sale triggers multiple coordinated actions across domains:
1. Product price retrieval (Product domain)
2. Revenue / discount calculation (Finance domain)
3. Inventory decrement (Inventory domain)
4. Transaction logging / ledger audit (Sales history domain)

The SalesService acts as an orchestrator that coordinates these steps while preserving
data integrity through database transaction management.
"""

from typing import List, Optional
from database.db import db
from models.sales import Sale
from services.product_service import ProductService
from services.inventory_service import InventoryService
from utils.helpers import ValidationError


class SalesService:
    """
    Orchestrates retail sales transactions, revenue computation, inventory updates,
    and historical sales reporting.
    """

    @staticmethod
    def calculate_sale_amount(
        unit_price: float, quantity: int, discount: float = 0.0
    ) -> float:
        """
        Pure business calculation: Computes total sale price after applying discounts.

        Formula:
            Subtotal = unit_price * quantity
            Discount Amount = Subtotal * (discount / 100)
            Final Total = Subtotal - Discount Amount

        Args:
            unit_price (float): Price of one unit in dollars/currency.
            quantity (int): Number of units purchased.
            discount (float, optional): Percentage discount (0 to 100). Defaults to 0.0.

        Returns:
            float: Rounded final total sale amount (2 decimal places).

        Raises:
            ValidationError: If inputs are negative or discount exceeds 100%.
        """
        if unit_price < 0:
            raise ValidationError("Unit price cannot be negative.")
        if quantity <= 0:
            raise ValidationError("Quantity must be at least 1.")
        if discount < 0 or discount > 100:
            raise ValidationError("Discount must be between 0% and 100%.")

        subtotal = unit_price * quantity
        discount_amount = subtotal * (discount / 100.0)
        final_amount = max(0.0, round(subtotal - discount_amount, 2))

        return final_amount

    @staticmethod
    def update_inventory_after_sale(product_id: int, quantity: int) -> None:
        """
        Inter-service communication: Communicates with InventoryService to deduct
        the sold units from available shelf stock.

        Args:
            product_id (int): Product identifier.
            quantity (int): Units sold to deduct.

        Raises:
            InsufficientStockError: If the store does not have enough units.
            ResourceNotFoundError: If the product does not exist.
        """
        # Delegate stock deduction to the specialized InventoryService
        InventoryService.decrease_stock(product_id=product_id, quantity=quantity)

    @staticmethod
    def create_sale(
        product_id: int, quantity: int, discount: float = 0.0
    ) -> Sale:
        """
        Executes a complete point-of-sale transaction.

        Workflow:
        1. Fetch current product information (to obtain accurate unit price).
        2. Calculate the total charge (including discount).
        3. Deduct stock through InventoryService (throws InsufficientStockError if out of stock).
        4. Create and persist the Sale audit record.
        5. Commit transaction. If any failure happens, rollback all changes.

        Args:
            product_id (int): ID of the product being purchased.
            quantity (int): Number of units to buy.
            discount (float, optional): Discount percentage. Defaults to 0.0.

        Returns:
            Sale: The saved Sale database entity.

        Raises:
            ResourceNotFoundError: If the product does not exist.
            InsufficientStockError: If inventory is lower than requested quantity.
            ValidationError: If parameters fail validation.
        """
        # Step 1: Input validation
        if quantity <= 0:
            raise ValidationError("Sale quantity must be at least 1 unit.")

        # Step 2: Fetch product details to retrieve current unit price
        product = ProductService.get_product_by_id(product_id)
        current_unit_price = product.price

        # Step 3: Compute the final sale revenue amount
        total_amount = SalesService.calculate_sale_amount(
            unit_price=current_unit_price, quantity=quantity, discount=discount
        )

        try:
            # Step 4: Update inventory (will fail if stock is insufficient)
            SalesService.update_inventory_after_sale(
                product_id=product_id, quantity=quantity
            )

            # Step 5: Record the transaction in the sales ledger
            new_sale = Sale(
                product_id=product_id,
                quantity=quantity,
                unit_price=current_unit_price,
                discount=discount,
                total_amount=total_amount,
            )

            db.session.add(new_sale)
            db.session.commit()

            return new_sale

        except Exception as e:
            # Atomic rollback: If recording the sale fails, revert any inventory deduction
            db.session.rollback()
            raise e

    @staticmethod
    def get_sales_history(product_id: Optional[int] = None) -> List[Sale]:
        """
        Retrieves historical sales transactions from the database.

        Args:
            product_id (Optional[int], optional): If provided, filters records to
                                                  sales of this product only.

        Returns:
            List[Sale]: List of Sale records, sorted newest to oldest.
        """
        query = Sale.query

        if product_id is not None:
            # Verify the product exists
            ProductService.get_product_by_id(product_id)
            query = query.filter_by(product_id=product_id)

        # Order chronological transactions from most recent to oldest
        return query.order_by(Sale.sale_date.desc()).all()
