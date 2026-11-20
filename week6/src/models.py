"""
Models for the Enterprise Order & Transaction Processing Pipeline.
Defines strongly-typed, immutable/validated data structures.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timezone
from enum import Enum


def _get_utc_now_str() -> str:
    """Helper to return ISO formatted UTC timestamp without deprecated methods."""
    return datetime.now(timezone.utc).isoformat()


class OrderStatus(Enum):
    """Enumeration of order lifecycle states."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class OrderItem:
    """Represents an individual line item inside a customer order."""
    item_id: str
    name: str
    unit_price: float
    quantity: int

    def __post_init__(self):
        if self.unit_price < 0:
            raise ValueError(f"unit_price must be non-negative, got {self.unit_price}")
        if self.quantity <= 0:
            raise ValueError(f"quantity must be greater than zero, got {self.quantity}")

    @property
    def total_price(self) -> float:
        """Computes the total line item price before order-level discounts."""
        return round(self.unit_price * self.quantity, 2)


@dataclass
class Customer:
    """Represents an authenticated customer entity."""
    customer_id: str
    name: str
    email: str
    tier: str = "STANDARD"

    def __post_init__(self):
        if not self.email or "@" not in self.email:
            raise ValueError(f"Invalid email address: {self.email}")
        if self.tier not in {"STANDARD", "SILVER", "GOLD", "PLATINUM"}:
            raise ValueError(f"Invalid customer tier: {self.tier}")


@dataclass
class Order:
    """Represents a customer purchase order containing line items, discount, and tax."""
    order_id: str
    customer_id: str
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    discount_pct: float = 0.0
    tax_rate: float = 0.05
    created_at: str = field(default_factory=_get_utc_now_str)

    def __post_init__(self):
        if self.discount_pct < 0 or self.discount_pct > 100:
            raise ValueError(f"discount_pct must be between 0 and 100, got {self.discount_pct}")
        if self.tax_rate < 0 or self.tax_rate > 1:
            raise ValueError(f"tax_rate must be between 0.0 and 1.0, got {self.tax_rate}")

    @property
    def subtotal(self) -> float:
        """Computes gross sum of all order line items."""
        return round(sum(item.total_price for item in self.items), 2)

    @property
    def discount_amount(self) -> float:
        """Computes discount deduction based on discount percentage."""
        return round(self.subtotal * (self.discount_pct / 100.0), 2)

    @property
    def taxable_subtotal(self) -> float:
        """Computes net subtotal subject to taxation."""
        return round(self.subtotal - self.discount_amount, 2)

    @property
    def tax_amount(self) -> float:
        """Computes tax applied on taxable subtotal."""
        return round(self.taxable_subtotal * self.tax_rate, 2)

    @property
    def grand_total(self) -> float:
        """Computes final amount payable."""
        return round(self.taxable_subtotal + self.tax_amount, 2)


@dataclass
class TransactionResult:
    """Represents the immutable audit record of a processed order transaction."""
    order_id: str
    customer_id: str
    status: OrderStatus
    subtotal: float
    discount_amount: float
    tax_amount: float
    grand_total: float
    processed_at: str
    notes: Optional[str] = None
