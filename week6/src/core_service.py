"""
Core Service for the Enterprise Order Processing and Analytics Engine.
Provides business logic for validating, calculating, discounting, and reporting orders.
"""
from typing import Dict, List, Optional
from datetime import datetime, timezone
from src.models import Order, OrderItem, Customer, OrderStatus, TransactionResult


def _current_timestamp() -> str:
    """Returns current ISO UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat()


class OrderProcessingService:
    """
    Business service managing customer orders, discounts, status transitions, and audit records.
    """

    TIER_DISCOUNTS = {
        "STANDARD": 0.0,
        "SILVER": 5.0,
        "GOLD": 10.0,
        "PLATINUM": 15.0
    }

    def __init__(self):
        self.customers: Dict[str, Customer] = {}
        self.orders: Dict[str, Order] = {}
        self.transactions: List[TransactionResult] = []

    def register_customer(self, customer_id: str, name: str, email: str, tier: str = "STANDARD") -> Customer:
        """Registers a new customer profile into the service directory."""
        if customer_id in self.customers:
            raise ValueError(f"Customer with ID '{customer_id}' already registered.")
        customer = Customer(customer_id=customer_id, name=name, email=email, tier=tier)
        self.customers[customer_id] = customer
        return customer

    def create_order(
        self,
        order_id: str,
        customer_id: str,
        items: List[OrderItem],
        discount_pct: Optional[float] = None
    ) -> Order:
        """Creates a pending order for an existing registered customer."""
        if order_id in self.orders:
            raise ValueError(f"Order with ID '{order_id}' already exists.")
        if customer_id not in self.customers:
            raise KeyError(f"Customer '{customer_id}' not found. Order cannot be created.")
        if not items:
            raise ValueError("Order must contain at least one item.")

        customer = self.customers[customer_id]
        if discount_pct is None:
            discount_pct = self.TIER_DISCOUNTS.get(customer.tier, 0.0)

        order = Order(
            order_id=order_id,
            customer_id=customer_id,
            items=list(items),
            status=OrderStatus.PENDING,
            discount_pct=discount_pct
        )
        self.orders[order_id] = order
        return order

    def process_order(self, order_id: str) -> TransactionResult:
        """Executes validation and financial processing on a pending order."""
        if order_id not in self.orders:
            raise KeyError(f"Order '{order_id}' not found.")

        order = self.orders[order_id]
        if order.status != OrderStatus.PENDING:
            raise RuntimeError(f"Order '{order_id}' is not in PENDING status (current: {order.status.value}).")

        order.status = OrderStatus.PROCESSING

        if order.grand_total <= 0:
            order.status = OrderStatus.FAILED
            tx = TransactionResult(
                order_id=order.order_id,
                customer_id=order.customer_id,
                status=OrderStatus.FAILED,
                subtotal=order.subtotal,
                discount_amount=order.discount_amount,
                tax_amount=order.tax_amount,
                grand_total=order.grand_total,
                processed_at=_current_timestamp(),
                notes="Order rejected: grand total must be positive."
            )
            self.transactions.append(tx)
            return tx

        order.status = OrderStatus.COMPLETED
        tx = TransactionResult(
            order_id=order.order_id,
            customer_id=order.customer_id,
            status=OrderStatus.COMPLETED,
            subtotal=order.subtotal,
            discount_amount=order.discount_amount,
            tax_amount=order.tax_amount,
            grand_total=order.grand_total,
            processed_at=_current_timestamp(),
            notes="Order processed successfully."
        )
        self.transactions.append(tx)
        return tx

    def cancel_order(self, order_id: str, reason: str = "User requested cancellation") -> Order:
        """Cancels a pending or processing order."""
        if order_id not in self.orders:
            raise KeyError(f"Order '{order_id}' not found.")
        order = self.orders[order_id]
        if order.status == OrderStatus.COMPLETED:
            raise RuntimeError(f"Cannot cancel completed order '{order_id}'.")
        order.status = OrderStatus.CANCELLED
        return order

    def compute_summary(self) -> Dict[str, float]:
        """Calculates aggregate business metrics across all settled transactions."""
        total_revenue = sum(tx.grand_total for tx in self.transactions if tx.status == OrderStatus.COMPLETED)
        total_discount = sum(tx.discount_amount for tx in self.transactions if tx.status == OrderStatus.COMPLETED)
        total_tax = sum(tx.tax_amount for tx in self.transactions if tx.status == OrderStatus.COMPLETED)
        completed_count = sum(1 for tx in self.transactions if tx.status == OrderStatus.COMPLETED)
        avg_order_value = round(total_revenue / completed_count, 2) if completed_count > 0 else 0.0

        return {
            "completed_orders": completed_count,
            "total_revenue": round(total_revenue, 2),
            "total_discounts_granted": round(total_discount, 2),
            "total_tax_collected": round(total_tax, 2),
            "average_order_value": avg_order_value
        }
