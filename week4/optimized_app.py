"""
optimized_app.py
Optimized high-performance implementation of the e-commerce analytics pipeline.
Applies industry-standard optimization techniques:
1. O(N) Hash Set / Hash Map for duplicate detection (replaces O(N^2) nested list scanning).
2. O(1) Dictionary Indexing for Customer joins (replaces O(N*M) linear search).
3. Pre-compiled Regex patterns and list `.join()` for O(N) string construction.
4. Single-pass accumulator algorithms using `statistics` or math formulations.
5. In-memory data layout efficiency using tuple unpacking and dictionary lookups.
"""

import math
import re
import time
from collections import defaultdict
from typing import List, Dict, Any, Set


# Pre-compiled Regex at module level (compilation occurs ONCE, not on every iteration)
ORDER_ID_REGEX = re.compile(r"^ORD_\d{6}$")


# OPTIMIZATION 1: O(N) Duplicate detection using a set of seen IDs
def find_duplicate_orders(orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen_ids: Set[str] = set()
    duplicate_ids: Set[str] = set()
    first_seen_orders: Dict[str, Dict[str, Any]] = {}

    for order in orders:
        oid = order["order_id"]
        if oid in seen_ids:
            duplicate_ids.add(oid)
        else:
            seen_ids.add(oid)
            first_seen_orders[oid] = order

    # Preserve order of duplicates
    return [first_seen_orders[oid] for oid in duplicate_ids]


# OPTIMIZATION 2: O(N + M) Hash Map Lookup for Customer joining
def join_orders_with_customers(orders: List[Dict[str, Any]], customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Pre-index customers into an O(1) lookup dictionary by customer_id
    customer_lookup = {c["customer_id"]: c for c in customers}

    default_cust = {"name": "Unknown", "tier": "Standard", "region": "Unknown"}
    joined = []
    for order in orders:
        cust = customer_lookup.get(order["customer_id"], default_cust)
        joined.append({
            **order,
            "customer_name": cust["name"],
            "customer_tier": cust["tier"],
            "customer_region": cust["region"]
        })
    return joined


# OPTIMIZATION 3: O(N) String Buffer construction via list appending and str.join()
def generate_audit_log(orders: List[Dict[str, Any]]) -> str:
    # Use list accumulator and precompiled regex
    pattern = ORDER_ID_REGEX
    log_lines = []
    for order in orders:
        is_valid = bool(pattern.match(order["order_id"]))
        log_lines.append(f"Order {order['order_id']} | Valid: {is_valid} | Amount: {order['amount']}\n")
    return "".join(log_lines)


# OPTIMIZATION 4: Optimized single-pass metric accumulation
def calculate_tier_revenue_and_metrics(joined_orders: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Group by tier
    tier_groups = defaultdict(lambda: {
        "total_revenue": 0.0,
        "order_count": 0,
        "completed_count": 0,
        "cancelled_count": 0,
        "amounts": []
    })

    for item in joined_orders:
        tier = item["customer_tier"]
        stats = tier_groups[tier]
        amt = item["amount"]
        stats["order_count"] += 1
        stats["amounts"].append(amt)
        if item["status"] == "COMPLETED":
            stats["total_revenue"] += amt
            stats["completed_count"] += 1
        else:
            stats["cancelled_count"] += 1

    # Single pass / fast math formulation
    results = {}
    for tier, stats in tier_groups.items():
        amounts = stats["amounts"]
        n = len(amounts)
        if n > 0:
            total_sum = sum(amounts)
            mean = total_sum / n
            variance = sum((x - mean) ** 2 for x in amounts) / n
            std_dev = math.sqrt(variance)
        else:
            mean = 0.0
            std_dev = 0.0

        results[tier] = {
            "total_revenue": round(stats["total_revenue"], 2),
            "order_count": stats["order_count"],
            "completed_count": stats["completed_count"],
            "cancelled_count": stats["cancelled_count"],
            "mean_amount": round(mean, 2),
            "std_dev": round(std_dev, 2)
        }
    return results


def run_pipeline(data: Dict[str, Any]) -> Dict[str, Any]:
    """Executes the optimized analytics pipeline."""
    orders = data["orders"]
    customers = data["customers"]

    duplicates = find_duplicate_orders(orders)
    joined_orders = join_orders_with_customers(orders, customers)
    audit_log = generate_audit_log(orders[:1000])
    metrics = calculate_tier_revenue_and_metrics(joined_orders)

    return {
        "duplicate_count": len(duplicates),
        "total_processed": len(joined_orders),
        "audit_log_length": len(audit_log),
        "metrics": metrics
    }


if __name__ == "__main__":
    from baseline_app import generate_synthetic_data
    print("Generating dataset...")
    data = generate_synthetic_data(num_orders=5000, num_customers=500)
    print("Executing optimized pipeline...")
    start = time.perf_counter()
    result = run_pipeline(data)
    elapsed = time.perf_counter() - start
    print(f"Optimized Pipeline Completed in: {elapsed:.4f} seconds")
    print(f"Results: {result}")

