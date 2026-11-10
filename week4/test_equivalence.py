"""
test_equivalence.py
Automated Verification Suite ensuring 100% functional equivalence and mathematical accuracy
between `baseline_app.py` and `optimized_app.py`.
Verifies that optimization did NOT alter any output results, counts, or metrics.
"""

import unittest
from baseline_app import (
    generate_synthetic_data,
    run_pipeline as baseline_run_pipeline,
    find_duplicate_orders as baseline_find_duplicates,
    join_orders_with_customers as baseline_join_customers,
    generate_audit_log as baseline_generate_audit,
    calculate_tier_revenue_and_metrics as baseline_tier_metrics
)
from optimized_app import (
    run_pipeline as optimized_run_pipeline,
    find_duplicate_orders as optimized_find_duplicates,
    join_orders_with_customers as optimized_join_customers,
    generate_audit_log as optimized_generate_audit,
    calculate_tier_revenue_and_metrics as optimized_tier_metrics
)


class TestOptimizationEquivalence(unittest.TestCase):
    """Rigorous verification tests to confirm exact functional parity between baseline & optimized."""

    @classmethod
    def setUpClass(cls):
        """Generate deterministic test dataset shared across tests."""
        cls.dataset = generate_synthetic_data(num_orders=2000, num_customers=200)
        cls.orders = cls.dataset["orders"]
        cls.customers = cls.dataset["customers"]

    def test_tc01_duplicate_orders_count_and_ids(self):
        """TC-01: Verify duplicate detection identifies exact same duplicate orders."""
        base_dups = baseline_find_duplicates(self.orders)
        opt_dups = optimized_find_duplicates(self.orders)

        self.assertEqual(len(base_dups), len(opt_dups), "Duplicate order count mismatch!")
        base_ids = set(d["order_id"] for d in base_dups)
        opt_ids = set(d["order_id"] for d in opt_dups)
        self.assertEqual(base_ids, opt_ids, "Duplicate order IDs must match exactly!")

    def test_tc02_join_orders_with_customers_equivalence(self):
        """TC-02: Verify joined customer fields (name, tier, region) match across all orders."""
        base_joined = baseline_join_customers(self.orders[:500], self.customers)
        opt_joined = optimized_join_customers(self.orders[:500], self.customers)

        self.assertEqual(len(base_joined), len(opt_joined))
        for b, o in zip(base_joined, opt_joined):
            self.assertEqual(b["order_id"], o["order_id"])
            self.assertEqual(b["customer_name"], o["customer_name"])
            self.assertEqual(b["customer_tier"], o["customer_tier"])
            self.assertEqual(b["customer_region"], o["customer_region"])

    def test_tc03_audit_log_string_parity(self):
        """TC-03: Verify generated audit log text is character-by-character identical."""
        base_log = baseline_generate_audit(self.orders[:200])
        opt_log = optimized_generate_audit(self.orders[:200])
        self.assertEqual(base_log, opt_log, "Audit log outputs must be identical!")

    def test_tc04_tier_metrics_exact_values(self):
        """TC-04: Verify revenues, order counts, means, and standard deviations match exactly."""
        base_joined = baseline_join_customers(self.orders, self.customers)
        opt_joined = optimized_join_customers(self.orders, self.customers)

        base_metrics = baseline_tier_metrics(base_joined)
        opt_metrics = optimized_tier_metrics(opt_joined)

        self.assertEqual(set(base_metrics.keys()), set(opt_metrics.keys()))
        for tier in base_metrics:
            b_stat = base_metrics[tier]
            o_stat = opt_metrics[tier]
            self.assertEqual(b_stat["total_revenue"], o_stat["total_revenue"])
            self.assertEqual(b_stat["order_count"], o_stat["order_count"])
            self.assertEqual(b_stat["completed_count"], o_stat["completed_count"])
            self.assertEqual(b_stat["cancelled_count"], o_stat["cancelled_count"])
            self.assertAlmostEqual(b_stat["mean_amount"], o_stat["mean_amount"], places=2)
            self.assertAlmostEqual(b_stat["std_dev"], o_stat["std_dev"], places=2)

    def test_tc05_end_to_end_pipeline_result_equivalence(self):
        """TC-05: Verify full macro-pipeline results match across baseline and optimized engines."""
        base_res = baseline_run_pipeline(self.dataset)
        opt_res = optimized_run_pipeline(self.dataset)

        self.assertEqual(base_res["duplicate_count"], opt_res["duplicate_count"])
        self.assertEqual(base_res["total_processed"], opt_res["total_processed"])
        self.assertEqual(base_res["audit_log_length"], opt_res["audit_log_length"])
        self.assertEqual(base_res["metrics"], opt_res["metrics"])

    def test_tc06_empty_dataset_boundary_handling(self):
        """TC-06: Verify edge case with zero orders and zero customers."""
        empty_data = {"orders": [], "customers": []}
        base_res = baseline_run_pipeline(empty_data)
        opt_res = optimized_run_pipeline(empty_data)
        self.assertEqual(base_res, opt_res)

    def test_tc07_single_order_boundary_handling(self):
        """TC-07: Verify edge case with a single order."""
        single_data = {
            "orders": [{"order_id": "ORD_000001", "customer_id": "CUST_001", "amount": 100.0, "status": "COMPLETED", "date": "2026-01-01", "items_count": 1}],
            "customers": [{"customer_id": "CUST_001", "name": "Alice", "tier": "VIP", "region": "North"}]
        }
        base_res = baseline_run_pipeline(single_data)
        opt_res = optimized_run_pipeline(single_data)
        self.assertEqual(base_res, opt_res)


if __name__ == "__main__":
    unittest.main()

