"""
module_logic.py
Core Business Logic for Finance Analysis Module.
Implements financial aggregation, category breakdown, query filtering,
CSV report generation, and account health analytics.
"""

import csv
import io
from typing import List, Dict, Optional, Tuple
from models import Transaction, TransactionType, AccountSummary


class FinanceAnalyzer:
    """
    Enterprise-grade financial computation and analytics engine.

    Provides operations for transaction ingestion, multi-currency rounding,
    balance computations, spending distribution analysis, search/filtering,
    and structured financial summary generation.
    """

    def __init__(self, initial_transactions: Optional[List[Transaction]] = None):
        """
        Initializes the analyzer with an optional pre-existing list of transactions.
        Avoids mutable default argument vulnerabilities.
        """
        self._transactions: List[Transaction] = []
        if initial_transactions is not None:
            for tx in initial_transactions:
                self.add_transaction(tx)

    @property
    def transactions(self) -> List[Transaction]:
        """Returns a defensive copy of the transaction records."""
        return list(self._transactions)

    def add_transaction(self, transaction: Transaction) -> None:
        """
        Ingests a verified Transaction into the ledger.

        Args:
            transaction (Transaction): Validated transaction instance.

        Raises:
            TypeError: If argument is not an instance of Transaction.
            ValueError: If a duplicate transaction_id already exists.
        """
        if not isinstance(transaction, Transaction):
            raise TypeError(
                f"Expected Transaction instance, received {type(transaction).__name__}"
            )

        if self.find_by_id(transaction.transaction_id) is not None:
            raise ValueError(
                f"Duplicate transaction_id '{transaction.transaction_id}' already exists."
            )

        self._transactions.append(transaction)

    def add_batch(self, transactions: List[Transaction]) -> int:
        """
        Batch-ingests multiple transactions atomically.
        If any transaction is invalid or duplicate, rolls back the entire batch.

        Args:
            transactions (List[Transaction]): List of transactions to add.

        Returns:
            int: Number of transactions added.
        """
        backup = list(self._transactions)
        try:
            for tx in transactions:
                self.add_transaction(tx)
            return len(transactions)
        except Exception as exc:
            self._transactions = backup
            raise exc

    def find_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Finds a transaction by its unique identifier."""
        clean_id = str(transaction_id).strip()
        for tx in self._transactions:
            if tx.transaction_id == clean_id:
                return tx
        return None

    def calculate_balance(self) -> float:
        """
        Calculates the net balance across all recorded transactions.
        Net Balance = Total Credits - Total Debits.

        Returns:
            float: Precision-rounded monetary balance to 2 decimal places.
        """
        balance = 0.0
        for tx in self._transactions:
            if tx.transaction_type == TransactionType.CREDIT:
                balance += tx.amount
            elif tx.transaction_type == TransactionType.DEBIT:
                balance -= tx.amount
        return round(balance, 2)

    def get_total_credits(self) -> float:
        """Returns total income (sum of all credit transactions)."""
        total = sum(tx.amount for tx in self._transactions if tx.transaction_type == TransactionType.CREDIT)
        return round(total, 2)

    def get_total_debits(self) -> float:
        """Returns total spending (sum of all debit transactions)."""
        total = sum(tx.amount for tx in self._transactions if tx.transaction_type == TransactionType.DEBIT)
        return round(total, 2)

    def get_category_totals(self) -> Dict[str, float]:
        """
        Aggregates total expenditures (debits) grouped by category.
        Credits are intentionally excluded from spending categorization.

        Returns:
            Dict[str, float]: Category name to total debit expense mapping.
        """
        totals: Dict[str, float] = {}
        for tx in self._transactions:
            if tx.transaction_type == TransactionType.DEBIT:
                totals[tx.category] = totals.get(tx.category, 0.0) + tx.amount
        return {cat: round(amt, 2) for cat, amt in totals.items()}

    def filter_transactions(
        self,
        transaction_type: Optional[TransactionType] = None,
        category: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[Transaction]:
        """
        Filters ledger by multi-conditional predicates.

        Args:
            transaction_type (Optional[TransactionType]): Filter by CREDIT or DEBIT.
            category (Optional[str]): Case-insensitive category match.
            min_amount (Optional[float]): Minimum transaction amount boundary.
            max_amount (Optional[float]): Maximum transaction amount boundary.

        Returns:
            List[Transaction]: Matching transaction records.
        """
        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            raise ValueError(
                f"min_amount ({min_amount}) cannot be greater than max_amount ({max_amount})"
            )

        results = self._transactions

        if transaction_type is not None:
            results = [tx for tx in results if tx.transaction_type == transaction_type]

        if category is not None:
            cat_clean = category.strip().lower()
            results = [tx for tx in results if tx.category.lower() == cat_clean]

        if min_amount is not None:
            results = [tx for tx in results if tx.amount >= min_amount]

        if max_amount is not None:
            results = [tx for tx in results if tx.amount <= max_amount]

        return list(results)

    def get_largest_expense(self) -> Optional[Transaction]:
        """
        Identifies the highest value debit transaction.

        Returns:
            Optional[Transaction]: Transaction record with maximum debit amount,
            or None if no debits exist.
        """
        debits = [tx for tx in self._transactions if tx.transaction_type == TransactionType.DEBIT]
        if not debits:
            return None
        return max(debits, key=lambda tx: tx.amount)

    def calculate_savings_rate(self) -> float:
        """
        Computes personal savings rate percentage: ((Credits - Debits) / Credits) * 100.

        Returns:
            float: Savings rate percentage rounded to 2 decimal places.
            Returns 0.0 if there are zero credits.
        """
        credits = self.get_total_credits()
        debits = self.get_total_debits()

        if credits <= 0:
            return 0.0

        savings = credits - debits
        rate = (savings / credits) * 100.0
        return round(rate, 2)

    def generate_summary(self) -> AccountSummary:
        """
        Synthesizes a full account summary snapshot integrating multiple financial metrics.

        Returns:
            AccountSummary: Complete analytics summary.
        """
        total_tx = len(self._transactions)
        total_amount = sum(tx.amount for tx in self._transactions)
        avg_tx = round(total_amount / total_tx, 2) if total_tx > 0 else 0.0

        return AccountSummary(
            total_balance=self.calculate_balance(),
            total_credits=self.get_total_credits(),
            total_debits=self.get_total_debits(),
            transaction_count=total_tx,
            category_breakdown=self.get_category_totals(),
            largest_expense=self.get_largest_expense(),
            average_transaction=avg_tx
        )

    def export_to_csv_string(self) -> str:
        """
        Exports the entire ledger into a formatted CSV string.

        Returns:
            str: CSV text content with header row.
        """
        output = io.StringIO()
        fieldnames = ["transaction_id", "amount", "transaction_type", "category", "description", "timestamp"]
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for tx in self._transactions:
            writer.writerow(tx.to_dict())
        return output.getvalue()
