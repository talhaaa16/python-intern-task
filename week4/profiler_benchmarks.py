"""
profiler_benchmarks.py
Comprehensive profiling and benchmarking harness comparing `baseline_app.py` and `optimized_app.py`.
Uses standard Python profiling tools:
- cProfile (Function call statistics, per-call timing, and cumulative time)
- timeit (Micro-benchmarking of individual algorithmic functions)
- pstats (Detailed bottleneck breakdown and call-tree analysis)
"""

import cProfile
import pstats
import io
import timeit
import json
from typing import Dict, Any

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


def profile_function_cprofile(func, *args, top_n: int = 10) -> str:
    """Profiles a function using cProfile and returns formatted pstats string."""
    pr = cProfile.Profile()
    pr.enable()
    func(*args)
    pr.disable()

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
    ps.print_stats(top_n)
    return s.getvalue()


def run_benchmarks(num_runs: int = 5) -> Dict[str, Any]:
    """Runs rigorous side-by-side timeit micro-benchmarks and macro-benchmarks."""
    print("=" * 80)
    print("      PERFORMANCE BENCHMARK & PROFILING HARNESS (cProfile & timeit)")
    print("=" * 80)

    print("\n[1/4] Generating standardized test dataset (5,000 orders, 500 customers)...")
    dataset = generate_synthetic_data(num_orders=5000, num_customers=500)
    orders = dataset["orders"]
    customers = dataset["customers"]
    joined_orders_base = baseline_join_customers(orders[:500], customers)
    joined_orders_opt = optimized_join_customers(orders[:500], customers)

    print("\n[2/4] Running Function-Level Micro-Benchmarks (timeit)...")

    # Benchmark 1: Duplicate Detection
    t_dup_base = timeit.timeit(lambda: baseline_find_duplicates(orders[:1000]), number=num_runs) / num_runs
    t_dup_opt = timeit.timeit(lambda: optimized_find_duplicates(orders[:1000]), number=num_runs) / num_runs
    speedup_dup = t_dup_base / t_dup_opt if t_dup_opt > 0 else float("inf")

    # Benchmark 2: Customer Joining
    t_join_base = timeit.timeit(lambda: baseline_join_customers(orders[:1000], customers), number=num_runs) / num_runs
    t_join_opt = timeit.timeit(lambda: optimized_join_customers(orders[:1000], customers), number=num_runs) / num_runs
    speedup_join = t_join_base / t_join_opt if t_join_opt > 0 else float("inf")

    # Benchmark 3: String Logging & Regex
    t_log_base = timeit.timeit(lambda: baseline_generate_audit(orders[:500]), number=num_runs) / num_runs
    t_log_opt = timeit.timeit(lambda: optimized_generate_audit(orders[:500]), number=num_runs) / num_runs
    speedup_log = t_log_base / t_log_opt if t_log_opt > 0 else float("inf")

    # Benchmark 4: Metric Calculation
    t_metric_base = timeit.timeit(lambda: baseline_tier_metrics(joined_orders_base), number=num_runs) / num_runs
    t_metric_opt = timeit.timeit(lambda: optimized_tier_metrics(joined_orders_opt), number=num_runs) / num_runs
    speedup_metric = t_metric_base / t_metric_opt if t_metric_opt > 0 else float("inf")

    # End-to-End Macro Benchmark
    print("\n[3/4] Running Full Pipeline Macro-Benchmarks...")
    t_macro_base = timeit.timeit(lambda: baseline_run_pipeline(dataset), number=3) / 3
    t_macro_opt = timeit.timeit(lambda: optimized_run_pipeline(dataset), number=3) / 3
    macro_speedup = t_macro_base / t_macro_opt if t_macro_opt > 0 else float("inf")

    # Output formatted comparison table
    print("\n" + "-" * 88)
    print(f"{'Pipeline Component':<30} | {'Baseline (s)':<15} | {'Optimized (s)':<15} | {'Speedup':<12}")
    print("-" * 88)
    print(f"{'1. Duplicate Detection':<30} | {t_dup_base:<15.6f} | {t_dup_opt:<15.6f} | {speedup_dup:<10.1f}x")
    print(f"{'2. Customer Join (O(N) vs Hash)':<30} | {t_join_base:<15.6f} | {t_join_opt:<15.6f} | {speedup_join:<10.1f}x")
    print(f"{'3. String Logging & Regex':<30} | {t_log_base:<15.6f} | {t_log_opt:<15.6f} | {speedup_log:<10.1f}x")
    print(f"{'4. Tier Metrics Calculation':<30} | {t_metric_base:<15.6f} | {t_metric_opt:<15.6f} | {speedup_metric:<10.1f}x")
    print("-" * 88)
    print(f"{'FULL END-TO-END PIPELINE':<30} | {t_macro_base:<15.6f} | {t_macro_opt:<15.6f} | {macro_speedup:<10.1f}x")
    print("-" * 88)

    print("\n[4/4] Generating cProfile Call-Tree Breakdown for Baseline Pipeline...")
    baseline_profile_str = profile_function_cprofile(baseline_run_pipeline, dataset, top_n=12)
    print(baseline_profile_str)

    print("\nGenerating cProfile Call-Tree Breakdown for Optimized Pipeline...")
    optimized_profile_str = profile_function_cprofile(optimized_run_pipeline, dataset, top_n=12)
    print(optimized_profile_str)

    return {
        "micro_benchmarks": {
            "duplicate_detection": {"baseline_s": t_dup_base, "optimized_s": t_dup_opt, "speedup": speedup_dup},
            "customer_join": {"baseline_s": t_join_base, "optimized_s": t_join_opt, "speedup": speedup_join},
            "audit_logging": {"baseline_s": t_log_base, "optimized_s": t_log_opt, "speedup": speedup_log},
            "tier_metrics": {"baseline_s": t_metric_base, "optimized_s": t_metric_opt, "speedup": speedup_metric}
        },
        "macro_benchmark": {
            "baseline_pipeline_s": t_macro_base,
            "optimized_pipeline_s": t_macro_opt,
            "overall_speedup": macro_speedup
        }
    }


if __name__ == "__main__":
    run_benchmarks()

