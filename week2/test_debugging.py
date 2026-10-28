"""
test_debugging.py
Automated Unit Tests Verifying All Bug Fixes in `corrected_app.py`.
Uses Python's built-in `unittest` framework.
"""

import unittest
import os
import tempfile
from corrected_app import InventoryManager, InventoryItem


class TestDebuggingAndFixes(unittest.TestCase):
    """Test suite ensuring all identified bugs have been successfully resolved."""

    def setUp(self):
        self.sample_items = [
            InventoryItem(id="101", name="Wireless Mouse", category="Electronics", price=25.0, stock=50),
            InventoryItem(id="102", name="Keyboard", category="Electronics", price=80.0, stock=0),
            InventoryItem(id="103", name="USB Cable", category="Accessories", price=10.0, stock=0),
            InventoryItem(id="104", name="Desk Lamp", category="Furniture", price=30.0, stock=15),
        ]
        self.manager = InventoryManager(inventory=self.sample_items)

    def test_fix_bug_1_instance_independence(self):
        """Verify that default instances do not share state (mutable default argument fixed)."""
        mgr1 = InventoryManager()
        mgr1.inventory.append(InventoryItem("999", "Leaked Item", "Misc", 5.0, 1))

        mgr2 = InventoryManager()
        self.assertEqual(len(mgr2.inventory), 0, "New InventoryManager should have empty inventory")
        self.assertEqual(len(mgr1.inventory), 1)

    def test_fix_bug_2_missing_file_handled_gracefully(self):
        """Verify that missing CSV files do not raise unhandled FileNotFoundError."""
        mgr = InventoryManager()
        result = mgr.load_from_csv("non_existent_file_12345.csv")
        self.assertFalse(result)
        self.assertEqual(len(mgr.inventory), 0)

    def test_fix_bug_3_display_inventory_no_index_error(self):
        """Verify that display_inventory runs without IndexError on any inventory size."""
        try:
            self.manager.display_inventory()
            empty_mgr = InventoryManager()
            empty_mgr.display_inventory()
        except IndexError:
            self.fail("display_inventory raised IndexError!")

    def test_fix_bug_4_and_5_order_processing_and_discount(self):
        """Verify proper type arithmetic, discount math, and stock reduction."""
        # Item 101: price $25.0, stock 50. Order 2 items with 10% discount:
        # Subtotal: $50.00, Discount: $5.00, Final: $45.00, Remaining stock: 48
        success = self.manager.process_order(item_id="101", quantity=2, discount_pct=10.0)
        self.assertTrue(success)
        self.assertEqual(self.manager.sales_history["101"], 45.0)

        item_101 = next(item for item in self.manager.inventory if item.id == "101")
        self.assertEqual(item_101.stock, 48)

    def test_fix_bug_6_remove_consecutive_out_of_stock_items(self):
        """Verify that consecutive out-of-stock items are all removed without index skipping."""
        removed = self.manager.remove_out_of_stock_items()
        self.assertEqual(removed, 2)
        remaining_ids = [item.id for item in self.manager.inventory]
        self.assertNotIn("102", remaining_ids)
        self.assertNotIn("103", remaining_ids)
        self.assertEqual(len(self.manager.inventory), 2)

    def test_fix_bug_7_calculate_average_empty_category_no_division_by_zero(self):
        """Verify calculate_average_price returns 0.0 without ZeroDivisionError."""
        avg = self.manager.calculate_average_price(category="NonExistentCategory")
        self.assertEqual(avg, 0.0)

        empty_mgr = InventoryManager()
        self.assertEqual(empty_mgr.calculate_average_price(), 0.0)

    def test_fix_bug_8_export_sales_report(self):
        """Verify that export_sales_report writes file properly using context manager."""
        self.manager.process_order("101", 1, 0)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_path = temp_file.name

        try:
            success = self.manager.export_sales_report(output_file=temp_path)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(temp_path))
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Item ID: 101", content)
                self.assertIn("Grand Total Revenue:", content)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
