"""
baseline_app.py
Original unoptimized implementation of an e-commerce customer transaction analytics pipeline.
Contains deliberate computational and algorithmic bottlenecks:
1. O(N^2) quadratic duplicate order detection via nested list loops.
2. Inefficient linear search O(N*M) for customer tier matching.
3. String concatenation in a loop (repeated memory reallocations).
4. Redundant re-computation inside loops (repeated regex compiling and calculations).
5. File I/O line-by-line parsing without buffered batch operations.
"""

import json
import math
import re
import time
from typing import List, Dict, Any


def generate_synthetic_data(num_orders: int = 5000, num_customers: int = 500) -> Dict[str, Any]:
    """Generates synthetic e-commerce orders and customer records deterministically."""
    customers = []
    for i in range(num_customers):
        tier = "VIP" if i % 10 == 0 else ("Gold" if i % 4 == 0 else "Regular")
        customers.append({
            "customer_id": f"CUST_{i:05d}",
            "name": f"Customer {i}",
            "tier": tier,
            "region": f"Region_{i % 5}"
        })

    orders = []
    for i in range(num_orders):
        cust_id = f"CUST_{(i % num_customers):05d}"
        orders.append({
            "order_id": f"ORD_{i:06d}",
            "customer_id": cust_id,
            "amount": round(10.0 + (i * 1.37) % 500.0, 2),
            "status": "COMPLETED" if i % 7 != 0 else "CANCELLED",
            "date": f"2026-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
            "items_count": (i % 8) + 1
        })

    # Deliberately inject 200 duplicate orders for testing duplicate detection
    for j in range(200):
        orders.append(dict(orders[j]))

    return {"customers": customers, "orders": orders}


# BOTTLENECK 1: O(N^2) Duplicate Detection using nested loops over lists
def find_duplicate_orders(orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    duplicates = []
    n = len(orders)
    for i in range(n):
        for j in range(i + 1, n):
            # Slow dict comparisons and nested iteration
            if orders[i]["order_id"] == orders[j]["order_id"]:
                is_already_added = False
                for d in duplicates:
                    if d["order_id"] == orders[i]["order_id"]:
                        is_already_added = True
                        break
                if not is_already_added:
                    duplicates.append(orders[i])
    return duplicates


# BOTTLENECK 2: O(N * M) Linear Search to join Customer information into Orders
def join_orders_with_customers(orders: List[Dict[str, Any]], customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    joined = []
    for order in orders:
        matched_cust = None
        # Inefficient linear scan through the customer list for every order
        for cust in customers:
            if cust["customer_id"] == order["customer_id"]:
                matched_cust = cust
                break
        
        item = dict(order)
        if matched_cust:
            item["customer_name"] = matched_cust["name"]
            item["customer_tier"] = matched_cust["tier"]
            item["customer_region"] = matched_cust["region"]
        else:
            item["customer_name"] = "Unknown"
            item["customer_tier"] = "Standard"
            item["customer_region"] = "Unknown"
        joined.append(item)
    return joined


# BOTTLENECK 3: Inefficient String Concatenation and Repeated Regex Compilation
def generate_audit_log(orders: List[Dict[str, Any]]) -> str:
    log_text = ""
    # Recompiling regex on EVERY single iteration!
    for order in orders:
        pattern = re.compile(r"^ORD_\d{6}$")
        is_valid = bool(pattern.match(order["order_id"]))
        # Quadratic string concatenation in a loop
        log_text = log_text + f"Order {order['order_id']} | Valid: {is_valid} | Amount: {order['amount']}\n"
    return log_text


# BOTTLENECK 4: Redundant Math Calculations inside loop
def calculate_tier_revenue_and_metrics(joined_orders: List[Dict[str, Any]]) -> Dict[str, Any]:
    tier_stats = {}
    for item in joined_orders:
        tier = item["customer_tier"]
        if tier not in tier_stats:
            tier_stats[tier] = {
                "total_revenue": 0.0,
                "order_count": 0,
                "completed_count": 0,
                "cancelled_count": 0,
                "amounts": []
            }
        
        tier_stats[tier]["order_count"] += 1
        tier_stats[tier]["amounts"].append(item["amount"])
        if item["status"] == "COMPLETED":
            tier_stats[tier]["total_revenue"] += item["amount"]
            tier_stats[tier]["completed_count"] += 1
        else:
            tier_stats[tier]["cancelled_count"] += 1

    # Inefficient metric calculation
    results = {}
    for tier, stats in tier_stats.items():
        amounts = stats["amounts"]
        n = len(amounts)
        mean = sum(amounts) / n if n > 0 else 0.0
        # Redundant two-pass variance calculation
        variance = 0.0
        for x in amounts:
            variance += (x - mean) ** 2
        std_dev = math.sqrt(variance / n) if n > 0 else 0.0
        
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
    """Executes the entire baseline analytics pipeline."""
    orders = data["orders"]
    customers = data["customers"]

    # Step 1: Detect duplicates
    duplicates = find_duplicate_orders(orders)

    # Step 2: Join customer information
    joined_orders = join_orders_with_customers(orders, customers)

    # Step 3: Generate audit logs
    audit_log = generate_audit_log(orders[:1000])  # limit to 1000 for realistic run time

    # Step 4: Tier metrics
    metrics = calculate_tier_revenue_and_metrics(joined_orders)

    return {
        "duplicate_count": len(duplicates),
        "total_processed": len(joined_orders),
        "audit_log_length": len(audit_log),
        "metrics": metrics
    }


if __name__ == "__main__":
    print("Generating dataset...")
    data = generate_synthetic_data(num_orders=5000, num_customers=500)
    print("Executing unoptimized baseline pipeline...")
    start = time.perf_counter()
    result = run_pipeline(data)
    elapsed = time.perf_counter() - start
    print(f"Baseline Pipeline Completed in: {elapsed:.4f} seconds")
    print(f"Results: {result}")

