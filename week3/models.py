"""
models.py
Domain models and enumerations for Finance Analysis Module.
Includes input validation, transaction filtering criteria, and structured summary models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime


class TransactionType(str, Enum):
    """Supported types of financial transactions."""
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class TransactionCategory(str, Enum):
    """Standardized financial transaction categories."""
    SALARY = "Salary"
    INVESTMENT = "Investment"
    FOOD = "Food & Dining"
    RENT = "Rent & Housing"
    UTILITIES = "Utilities"
    TRAVEL = "Travel & Transit"
    ENTERTAINMENT = "Entertainment"
    HEALTHCARE = "Healthcare"
    OTHER = "Other"


@dataclass
class Transaction:
    """
    Represents an immutable, validated financial transaction record.

    Attributes:
        transaction_id (str): Unique transaction identifier.
        amount (float): Monetary value of transaction. Must be strictly positive (> 0.00).
        transaction_type (TransactionType): CREDIT or DEBIT.
        category (str): Category grouping (e.g. Food, Rent, Salary).
        description (str): Human-readable note.
        timestamp (str): ISO-8601 string representation of transaction date-time.
    """
    transaction_id: str
    amount: float
    transaction_type: TransactionType
    category: str = "Other"
    description: str = ""
    timestamp: str = ""

    def __post_init__(self):
        # Transaction ID validation
        if not isinstance(self.transaction_id, str) or not self.transaction_id.strip():
            raise ValueError("transaction_id must be a non-empty string.")
        self.transaction_id = self.transaction_id.strip()

        # Amount validation: must be numeric and strictly positive
        if not isinstance(self.amount, (int, float)):
            raise TypeError(f"Amount must be a numeric value, got {type(self.amount).__name__}.")
        if self.amount <= 0:
            raise ValueError(f"Transaction amount must be strictly greater than zero. Received: {self.amount}")
        self.amount = round(float(self.amount), 2)

        # Type validation
        if isinstance(self.transaction_type, str):
            try:
                self.transaction_type = TransactionType(self.transaction_type.upper().strip())
            except ValueError:
                raise ValueError(
                    f"Invalid transaction_type '{self.transaction_type}'. Must be CREDIT or DEBIT."
                )
        elif not isinstance(self.transaction_type, TransactionType):
            raise TypeError("transaction_type must be an instance of TransactionType or valid string.")

        # Category normalization
        if not isinstance(self.category, str) or not self.category.strip():
            self.category = "Other"
        else:
            self.category = self.category.strip()

        # Description normalization
        self.description = self.description.strip() if isinstance(self.description, str) else ""

        # Timestamp default
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict:
        """Serializes Transaction to dictionary format."""
        return {
            "transaction_id": self.transaction_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type.value,
            "category": self.category,
            "description": self.description,
            "timestamp": self.timestamp,
        }


@dataclass
class AccountSummary:
    """
    Aggregated financial snapshot representation.

    Attributes:
        total_balance (float): Net balance (Credits - Debits).
        total_credits (float): Sum of all credit transactions.
        total_debits (float): Sum of all debit transactions.
        transaction_count (int): Total number of transactions processed.
        category_breakdown (Dict[str, float]): Total debit expenditures per category.
        largest_expense (Optional[Transaction]): Single largest debit transaction.
        average_transaction (float): Average value across all transactions.
    """
    total_balance: float
    total_credits: float
    total_debits: float
    transaction_count: int = 0
    category_breakdown: Dict[str, float] = field(default_factory=dict)
    largest_expense: Optional[Transaction] = None
    average_transaction: float = 0.0

    def to_dict(self) -> dict:
        """Serializes AccountSummary to dictionary format."""
        return {
            "total_balance": round(self.total_balance, 2),
            "total_credits": round(self.total_credits, 2),
            "total_debits": round(self.total_debits, 2),
            "transaction_count": self.transaction_count,
            "category_breakdown": self.category_breakdown,
            "largest_expense": self.largest_expense.to_dict() if self.largest_expense else None,
            "average_transaction": round(self.average_transaction, 2),
        }
