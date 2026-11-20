"""
Automated Unit and Integration Test Suite for Continuous Integration Verification.
Verifies business logic, boundary conditions, edge cases, exceptions, and analytics.
"""
import os
import sys
import unittest

# Ensure week6 root is in sys.path regardless of runner working directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.models import Customer, Order, OrderItem, OrderStatus, TransactionResult
from src.core_service import OrderProcessingService


class TestCustomerModels(unittest.TestCase):
    """
    Unit tests for Customer data model validation.
    """

    def test_valid_customer_creation(self):
        """Test valid customer creation across supported tiers."""
        c = Customer(customer_id="CUST-001", name="Alice Smith", email="alice@example.com", tier="GOLD")
        self.assertEqual(c.customer_id, "CUST-001")
        self.assertEqual(c.tier, "GOLD")

    def test_invalid_email_format(self):
        """Test that missing '@' symbol in email raises ValueError."""
        with self.assertRaises(ValueError):
            Customer(customer_id="CUST-002", name="Bad Email", email="invalid-email-address")

    def test_invalid_customer_tier(self):
        """Test that unknown tier raises ValueError."""
        with self.assertRaises(ValueError):
            Customer(customer_id="CUST-003", name="Invalid Tier", email="test@example.com", tier="DIAMOND")


class TestOrderItemModels(unittest.TestCase):
    """
    Unit tests for OrderItem data model validation and calculations.
    """

    def test_order_item_total_calculation(self):
        """Test calculation of total_price for valid quantity and unit_price."""
        item = OrderItem(item_id="ITEM-1", name="Widget", unit_price=12.50, quantity=4)
        self.assertEqual(item.total_price, 50.00)

    def test_negative_unit_price(self):
        """Test that negative unit_price raises ValueError."""
        with self.assertRaises(ValueError):
            OrderItem(item_id="ITEM-2", name="Negative Item", unit_price=-5.0, quantity=1)

    def test_zero_or_negative_quantity(self):
        """Test that zero or negative quantity raises ValueError."""
        with self.assertRaises(ValueError):
            OrderItem(item_id="ITEM-3", name="Zero Qty", unit_price=10.0, quantity=0)
        with self.assertRaises(ValueError):
            OrderItem(item_id="ITEM-4", name="Neg Qty", unit_price=10.0, quantity=-2)


class TestOrderCalculations(unittest.TestCase):
    """
    Unit tests for Order financial computations including discounts and taxes.
    """

    def test_order_financial_computations_without_discount(self):
        """Test subtotal, tax, and grand total calculations without discount."""
        items = [
            OrderItem(item_id="I-1", name="Keyboard", unit_price=50.00, quantity=2),  # 100
            OrderItem(item_id="I-2", name="Mouse", unit_price=25.00, quantity=1),     # 25
        ]
        order = Order(order_id="ORD-100", customer_id="CUST-001", items=items, discount_pct=0.0, tax_rate=0.05)
        self.assertEqual(order.subtotal, 125.00)
        self.assertEqual(order.discount_amount, 0.00)
        self.assertEqual(order.taxable_subtotal, 125.00)
        self.assertEqual(order.tax_amount, 6.25)
        self.assertEqual(order.grand_total, 131.25)

    def test_order_financial_computations_with_discount(self):
        """Test subtotal, discount, tax, and grand total calculations with 10% discount."""
        items = [
            OrderItem(item_id="I-1", name="Monitor", unit_price=200.00, quantity=1)
        ]
        order = Order(order_id="ORD-101", customer_id="CUST-001", items=items, discount_pct=10.0, tax_rate=0.05)
        self.assertEqual(order.subtotal, 200.00)
        self.assertEqual(order.discount_amount, 20.00)
        self.assertEqual(order.taxable_subtotal, 180.00)
        self.assertEqual(order.tax_amount, 9.00)
        self.assertEqual(order.grand_total, 189.00)

    def test_invalid_discount_range(self):
        """Test that out-of-bounds discount percentages raise ValueError."""
        with self.assertRaises(ValueError):
            Order(order_id="ORD-102", customer_id="CUST-001", discount_pct=-5.0)
        with self.assertRaises(ValueError):
            Order(order_id="ORD-103", customer_id="CUST-001", discount_pct=105.0)


class TestOrderProcessingService(unittest.TestCase):
    """
    Integration tests for OrderProcessingService business workflow.
    """

    def setUp(self):
        """Set up test environment with registered customers."""
        self.service = OrderProcessingService()
        self.service.register_customer("C-1", "Standard User", "std@test.com", "STANDARD")
        self.service.register_customer("C-2", "Gold User", "gold@test.com", "GOLD")

    def test_duplicate_customer_registration_fails(self):
        """Test that registering duplicate customer IDs raises ValueError."""
        with self.assertRaises(ValueError):
            self.service.register_customer("C-1", "Duplicate", "dup@test.com")

    def test_create_order_for_unknown_customer_fails(self):
        """Test that creating an order for an unlisted customer raises KeyError."""
        items = [OrderItem(item_id="I-1", name="Laptop", unit_price=1000.0, quantity=1)]
        with self.assertRaises(KeyError):
            self.service.create_order("ORD-X", "NON-EXISTENT", items)

    def test_create_order_empty_items_fails(self):
        """Test that creating an order with no items raises ValueError."""
        with self.assertRaises(ValueError):
            self.service.create_order("ORD-EMPTY", "C-1", [])

    def test_automatic_tier_discount_application(self):
        """Test that customer tier discount is automatically applied when discount_pct is omitted."""
        items = [OrderItem(item_id="I-1", name="Tablet", unit_price=500.0, quantity=1)]
        order = self.service.create_order("ORD-TIER", "C-2", items)
        # Gold user gets 10.0% discount
        self.assertEqual(order.discount_pct, 10.0)
        self.assertEqual(order.discount_amount, 50.0)

    def test_successful_order_processing(self):
        """Test end-to-end order processing lifecycle from PENDING to COMPLETED."""
        items = [OrderItem(item_id="I-1", name="Desk", unit_price=150.0, quantity=2)]
        self.service.create_order("ORD-PROC", "C-1", items)
        tx = self.service.process_order("ORD-PROC")
        self.assertEqual(tx.status, OrderStatus.COMPLETED)
        self.assertEqual(self.service.orders["ORD-PROC"].status, OrderStatus.COMPLETED)
        self.assertEqual(tx.grand_total, 315.0)  # 300 subtotal + 5% tax

    def test_process_non_pending_order_fails(self):
        """Test that processing an already completed order raises RuntimeError."""
        items = [OrderItem(item_id="I-1", name="Desk", unit_price=100.0, quantity=1)]
        self.service.create_order("ORD-ONCE", "C-1", items)
        self.service.process_order("ORD-ONCE")
        with self.assertRaises(RuntimeError):
            self.service.process_order("ORD-ONCE")

    def test_order_cancellation(self):
        """Test cancelling a pending order and preventing cancellation of completed order."""
        items = [OrderItem(item_id="I-1", name="Desk", unit_price=100.0, quantity=1)]
        order = self.service.create_order("ORD-CANCEL", "C-1", items)
        self.service.cancel_order("ORD-CANCEL")
        self.assertEqual(order.status, OrderStatus.CANCELLED)

        # Cannot cancel completed order
        self.service.create_order("ORD-COMP", "C-1", items)
        self.service.process_order("ORD-COMP")
        with self.assertRaises(RuntimeError):
            self.service.cancel_order("ORD-COMP")

    def test_compute_summary_analytics(self):
        """Test analytics summary calculation across multiple transactions."""
        items1 = [OrderItem(item_id="I-1", name="Pen", unit_price=10.0, quantity=10)]
        items2 = [OrderItem(item_id="I-2", name="Book", unit_price=20.0, quantity=5)]

        self.service.create_order("O-1", "C-1", items1)
        self.service.create_order("O-2", "C-2", items2)

        self.service.process_order("O-1")
        self.service.process_order("O-2")

        summary = self.service.compute_summary()
        self.assertEqual(summary["completed_orders"], 2)
        self.assertGreater(summary["total_revenue"], 0)
        self.assertGreater(summary["average_order_value"], 0)


if __name__ == "__main__":
    unittest.main()

