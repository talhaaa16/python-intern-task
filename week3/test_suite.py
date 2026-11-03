"""
test_suite.py
Comprehensive Automated Test Suite for Finance Analysis Module.
Covers:
- Unit Tests (models, validation, calculations, edge cases, error conditions)
- Integration Tests (summary generation, multi-component pipelines, batch operations)
- Parameterized Tests (boundary conditions, floating point precision)
Uses Python's native `unittest` framework (100% self-contained, 0 dependencies).
"""

import unittest
from datetime import datetime
from models import Transaction, TransactionType, TransactionCategory, AccountSummary
from module_logic import FinanceAnalyzer


class TestTransactionModel(unittest.TestCase):
    """Unit tests validating domain models, attributes, constraints, and edge cases."""

    def test_tc01_valid_credit_transaction(self):
        """TC-01: Valid CREDIT transaction creation and attribute population."""
        tx = Transaction("TX-100", 2500.50, TransactionType.CREDIT, "Salary", "October Paycheck")
        self.assertEqual(tx.transaction_id, "TX-100")
        self.assertEqual(tx.amount, 2500.50)
        self.assertEqual(tx.transaction_type, TransactionType.CREDIT)
        self.assertEqual(tx.category, "Salary")
        self.assertEqual(tx.description, "October Paycheck")
        self.assertTrue(len(tx.timestamp) > 0)

    def test_tc02_valid_debit_transaction(self):
        """TC-02: Valid DEBIT transaction creation."""
        tx = Transaction("TX-101", 85.25, TransactionType.DEBIT, "Food & Dining", "Grocery Shopping")
        self.assertEqual(tx.transaction_type, TransactionType.DEBIT)
        self.assertEqual(tx.amount, 85.25)

    def test_tc03_string_type_coercion_and_normalization(self):
        """TC-03: String value 'credit' or 'DEBIT' coerced into TransactionType enum."""
        tx_cred = Transaction("TX-102", 100.0, "credit", "Bonus", "Perf bonus")
        tx_deb = Transaction("TX-103", 45.0, " DEBIT ", "Books", "Python book")
        self.assertEqual(tx_cred.transaction_type, TransactionType.CREDIT)
        self.assertEqual(tx_deb.transaction_type, TransactionType.DEBIT)

    def test_tc04_amount_zero_rejected(self):
        """TC-04: Boundary Edge Case - Zero monetary amount (0.00) must raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            Transaction("TX-104", 0.00, TransactionType.CREDIT, "Gift")
        self.assertIn("strictly greater than zero", str(ctx.exception))

    def test_tc05_negative_amount_rejected(self):
        """TC-05: Negative monetary amount must raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            Transaction("TX-105", -500.00, TransactionType.DEBIT, "Misc")
        self.assertIn("strictly greater than zero", str(ctx.exception))

    def test_tc06_non_numeric_amount_rejected(self):
        """TC-06: Non-numeric amounts (e.g. 'one hundred') raise TypeError."""
        with self.assertRaises(TypeError):
            Transaction("TX-106", "100.00", TransactionType.CREDIT)  # string amount

    def test_tc07_empty_transaction_id_rejected(self):
        """TC-07: Blank or whitespace-only transaction_id must raise ValueError."""
        with self.assertRaises(ValueError):
            Transaction("", 100.0, TransactionType.CREDIT)
        with self.assertRaises(ValueError):
            Transaction("   ", 100.0, TransactionType.CREDIT)

    def test_tc08_invalid_transaction_type_string_rejected(self):
        """TC-08: Unrecognized transaction type strings raise ValueError."""
        with self.assertRaises(ValueError):
            Transaction("TX-108", 100.0, "TRANSFER")

    def test_tc09_default_category_fallback(self):
        """TC-09: Unspecified or empty category safely defaults to 'Other'."""
        tx = Transaction("TX-109", 10.0, TransactionType.DEBIT, "")
        self.assertEqual(tx.category, "Other")

    def test_tc10_transaction_to_dict_serialization(self):
        """TC-10: Verify to_dict structure and values."""
        tx = Transaction("TX-110", 75.0, TransactionType.DEBIT, "Utilities", "Electricity", "2026-10-01 12:00:00")
        d = tx.to_dict()
        self.assertEqual(d["transaction_id"], "TX-110")
        self.assertEqual(d["amount"], 75.0)
        self.assertEqual(d["transaction_type"], "DEBIT")
        self.assertEqual(d["category"], "Utilities")


class TestFinanceAnalyzerUnit(unittest.TestCase):
    """Unit tests for individual methods within FinanceAnalyzer."""

    def setUp(self):
        """Initialize a fresh analyzer instance before each test."""
        self.analyzer = FinanceAnalyzer()

    def test_tc11_initial_state_empty(self):
        """TC-11: New analyzer instance starts with 0 transactions and 0.00 balance."""
        self.assertEqual(len(self.analyzer.transactions), 0)
        self.assertEqual(self.analyzer.calculate_balance(), 0.0)
        self.assertEqual(self.analyzer.get_total_credits(), 0.0)
        self.assertEqual(self.analyzer.get_total_debits(), 0.0)

    def test_tc12_add_transaction_success(self):
        """TC-12: Adding transaction appends to collection."""
        tx = Transaction("TX-201", 500.0, TransactionType.CREDIT, "Salary")
        self.analyzer.add_transaction(tx)
        self.assertEqual(len(self.analyzer.transactions), 1)
        self.assertEqual(self.analyzer.transactions[0].transaction_id, "TX-201")

    def test_tc13_add_non_transaction_type_error(self):
        """TC-13: Ingesting raw dictionary or incompatible type raises TypeError."""
        with self.assertRaises(TypeError):
            self.analyzer.add_transaction({"amount": 100})  # type: ignore

    def test_tc14_duplicate_transaction_id_rejected(self):
        """TC-14: Adding two transactions with identical IDs raises ValueError."""
        tx1 = Transaction("DUP-01", 100.0, TransactionType.CREDIT)
        tx2 = Transaction("DUP-01", 200.0, TransactionType.DEBIT)
        self.analyzer.add_transaction(tx1)
        with self.assertRaises(ValueError) as ctx:
            self.analyzer.add_transaction(tx2)
        self.assertIn("already exists", str(ctx.exception))
        self.assertEqual(len(self.analyzer.transactions), 1)

    def test_tc15_calculate_balance_credits_only(self):
        """TC-15: Balance calculation with only credits."""
        self.analyzer.add_transaction(Transaction("T1", 1200.50, TransactionType.CREDIT))
        self.analyzer.add_transaction(Transaction("T2", 300.25, TransactionType.CREDIT))
        self.assertEqual(self.analyzer.calculate_balance(), 1500.75)
        self.assertEqual(self.analyzer.get_total_credits(), 1500.75)
        self.assertEqual(self.analyzer.get_total_debits(), 0.0)

    def test_tc16_calculate_balance_debits_only(self):
        """TC-16: Balance calculation with only debits results in negative balance."""
        self.analyzer.add_transaction(Transaction("T1", 45.00, TransactionType.DEBIT))
        self.analyzer.add_transaction(Transaction("T2", 55.50, TransactionType.DEBIT))
        self.assertEqual(self.analyzer.calculate_balance(), -100.50)
        self.assertEqual(self.analyzer.get_total_debits(), 100.50)

    def test_tc17_floating_point_precision_rounding(self):
        """TC-17: Complex floating point addition (0.1 + 0.2) rounded cleanly to 2 decimals."""
        self.analyzer.add_transaction(Transaction("T1", 0.10, TransactionType.CREDIT))
        self.analyzer.add_transaction(Transaction("T2", 0.20, TransactionType.CREDIT))
        self.assertEqual(self.analyzer.calculate_balance(), 0.30)

    def test_tc18_category_totals_debits_only(self):
        """TC-18: Spending categorization only aggregates DEBIT transactions."""
        self.analyzer.add_transaction(Transaction("T1", 120.0, TransactionType.DEBIT, "Food & Dining"))
        self.analyzer.add_transaction(Transaction("T2", 35.50, TransactionType.DEBIT, "Food & Dining"))
        self.analyzer.add_transaction(Transaction("T3", 75.0, TransactionType.DEBIT, "Utilities"))
        self.analyzer.add_transaction(Transaction("T4", 3000.0, TransactionType.CREDIT, "Food & Dining"))  # credit should NOT count

        totals = self.analyzer.get_category_totals()
        self.assertEqual(totals["Food & Dining"], 155.50)
        self.assertEqual(totals["Utilities"], 75.00)
        self.assertNotIn("Salary", totals)

    def test_tc19_category_totals_empty_when_no_debits(self):
        """TC-19: Category totals dictionary is empty when no debits exist."""
        self.analyzer.add_transaction(Transaction("T1", 500.0, TransactionType.CREDIT, "Salary"))
        self.assertEqual(self.analyzer.get_category_totals(), {})

    def test_tc20_filter_by_type(self):
        """TC-20: Filter transactions by transaction_type (CREDIT vs DEBIT)."""
        self.analyzer.add_transaction(Transaction("T1", 100.0, TransactionType.CREDIT))
        self.analyzer.add_transaction(Transaction("T2", 50.0, TransactionType.DEBIT))
        self.analyzer.add_transaction(Transaction("T3", 75.0, TransactionType.CREDIT))

        credits = self.analyzer.filter_transactions(transaction_type=TransactionType.CREDIT)
        debits = self.analyzer.filter_transactions(transaction_type=TransactionType.DEBIT)
        self.assertEqual(len(credits), 2)
        self.assertEqual(len(debits), 1)

    def test_tc21_filter_by_category_case_insensitive(self):
        """TC-21: Filter transactions by category matching case-insensitively."""
        self.analyzer.add_transaction(Transaction("T1", 50.0, TransactionType.DEBIT, "Travel"))
        self.analyzer.add_transaction(Transaction("T2", 30.0, TransactionType.DEBIT, "travel"))
        self.analyzer.add_transaction(Transaction("T3", 20.0, TransactionType.DEBIT, "Food"))

        travel_txs = self.analyzer.filter_transactions(category="TRAVEL")
        self.assertEqual(len(travel_txs), 2)

    def test_tc22_filter_by_amount_range(self):
        """TC-22: Filter transactions by min_amount and max_amount."""
        self.analyzer.add_transaction(Transaction("T1", 10.0, TransactionType.DEBIT))
        self.analyzer.add_transaction(Transaction("T2", 50.0, TransactionType.DEBIT))
        self.analyzer.add_transaction(Transaction("T3", 150.0, TransactionType.DEBIT))

        filtered = self.analyzer.filter_transactions(min_amount=20.0, max_amount=100.0)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].transaction_id, "T2")

    def test_tc23_filter_invalid_amount_range_raises_error(self):
        """TC-23: Filter with min_amount > max_amount raises ValueError."""
        with self.assertRaises(ValueError):
            self.analyzer.filter_transactions(min_amount=100.0, max_amount=50.0)

    def test_tc24_get_largest_expense(self):
        """TC-24: Correctly identifies single highest debit expense."""
        self.analyzer.add_transaction(Transaction("T1", 45.0, TransactionType.DEBIT, "Dining"))
        self.analyzer.add_transaction(Transaction("T2", 1200.0, TransactionType.DEBIT, "Rent"))
        self.analyzer.add_transaction(Transaction("T3", 250.0, TransactionType.DEBIT, "Utilities"))
        self.analyzer.add_transaction(Transaction("T4", 5000.0, TransactionType.CREDIT, "Salary"))  # Higher, but credit!

        largest = self.analyzer.get_largest_expense()
        self.assertIsNotNone(largest)
        self.assertEqual(largest.transaction_id, "T2")
        self.assertEqual(largest.amount, 1200.0)

    def test_tc25_get_largest_expense_none_when_no_debits(self):
        """TC-25: get_largest_expense returns None if no debits exist."""
        self.analyzer.add_transaction(Transaction("T1", 5000.0, TransactionType.CREDIT))
        self.assertIsNone(self.analyzer.get_largest_expense())

    def test_tc26_calculate_savings_rate(self):
        """TC-26: Savings rate calculation ((Credits - Debits) / Credits) * 100."""
        # Income = 4000, Expenses = 1000 => Savings = 3000 (75.0%)
        self.analyzer.add_transaction(Transaction("T1", 4000.0, TransactionType.CREDIT))
        self.analyzer.add_transaction(Transaction("T2", 1000.0, TransactionType.DEBIT))
        self.assertEqual(self.analyzer.calculate_savings_rate(), 75.0)

    def test_tc27_savings_rate_zero_when_no_income(self):
        """TC-27: Savings rate returns 0.0 when credits are zero, avoiding ZeroDivisionError."""
        self.analyzer.add_transaction(Transaction("T1", 500.0, TransactionType.DEBIT))
        self.assertEqual(self.analyzer.calculate_savings_rate(), 0.0)


class TestFinanceAnalyzerIntegration(unittest.TestCase):
    """Integration tests verifying end-to-end workflows and multi-component pipelines."""

    def setUp(self):
        self.analyzer = FinanceAnalyzer()

    def test_tc28_batch_ingestion_atomic_success(self):
        """TC-28: Batch ingestion adds all transactions atomically."""
        batch = [
            Transaction("B1", 1500.0, TransactionType.CREDIT, "Salary"),
            Transaction("B2", 450.0, TransactionType.DEBIT, "Rent"),
            Transaction("B3", 75.50, TransactionType.DEBIT, "Groceries")
        ]
        count = self.analyzer.add_batch(batch)
        self.assertEqual(count, 3)
        self.assertEqual(len(self.analyzer.transactions), 3)
        self.assertEqual(self.analyzer.calculate_balance(), 974.50)

    def test_tc29_batch_ingestion_rollback_on_failure(self):
        """TC-29: Batch ingestion transaction rollback on duplicate ID within batch."""
        self.analyzer.add_transaction(Transaction("PRE-1", 100.0, TransactionType.CREDIT))

        faulty_batch = [
            Transaction("B1", 200.0, TransactionType.CREDIT),
            Transaction("PRE-1", 300.0, TransactionType.CREDIT)  # Duplicate!
        ]

        with self.assertRaises(ValueError):
            self.analyzer.add_batch(faulty_batch)

        # Rollback check: initial state preserved
        self.assertEqual(len(self.analyzer.transactions), 1)
        self.assertEqual(self.analyzer.transactions[0].transaction_id, "PRE-1")

    def test_tc30_generate_summary_integration(self):
        """TC-30: Comprehensive AccountSummary snapshot generation."""
        dataset = [
            Transaction("T1", 5000.0, TransactionType.CREDIT, "Salary"),
            Transaction("T2", 1500.0, TransactionType.DEBIT, "Rent"),
            Transaction("T3", 250.0, TransactionType.DEBIT, "Food"),
            Transaction("T4", 150.0, TransactionType.DEBIT, "Food"),
            Transaction("T5", 500.0, TransactionType.CREDIT, "Investment"),
        ]
        self.analyzer.add_batch(dataset)

        summary = self.analyzer.generate_summary()
        self.assertIsInstance(summary, AccountSummary)
        self.assertEqual(summary.total_credits, 5500.0)
        self.assertEqual(summary.total_debits, 1900.0)
        self.assertEqual(summary.total_balance, 3600.0)
        self.assertEqual(summary.transaction_count, 5)
        self.assertEqual(summary.category_breakdown["Food"], 400.0)
        self.assertEqual(summary.category_breakdown["Rent"], 1500.0)
        self.assertIsNotNone(summary.largest_expense)
        self.assertEqual(summary.largest_expense.transaction_id, "T2")
        self.assertEqual(summary.average_transaction, 1480.0)  # (5000+1500+250+150+500)/5 = 7400/5

    def test_tc31_export_csv_roundtrip_integration(self):
        """TC-31: Export to CSV string matches transaction attributes and formatting."""
        self.analyzer.add_transaction(Transaction("CSV-1", 100.0, TransactionType.CREDIT, "Salary", "Test CSV"))
        csv_text = self.analyzer.export_to_csv_string()
        self.assertIn("transaction_id,amount,transaction_type,category,description,timestamp", csv_text)
        self.assertIn("CSV-1,100.0,CREDIT,Salary,Test CSV", csv_text)


if __name__ == "__main__":
    unittest.main()
