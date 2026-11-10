# Week 4: Performance Optimization in Python Applications

A high-performance algorithmic engineering and profiling project demonstrating baseline performance analysis, bottleneck diagnosis with `cProfile`, algorithmic refactoring, and quantitative benchmarking with `timeit`.

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Folder & File Structure](#folder--file-structure)
3. [Summary of Identified Bottlenecks & Fixes](#summary-of-identified-bottlenecks--fixes)
4. [Quantitative Performance Comparison](#quantitative-performance-comparison)
5. [How to Run Benchmarks, Profilers & Tests](#how-to-run-benchmarks-profilers--tests)
6. [Full Evaluation Criteria Compliance Checklist (Items 1–18)](#full-evaluation-criteria-compliance-checklist-items-118)

---

## 1. Project Overview
This project satisfies all requirements for **Week 4 Task: Performance Optimization in Python Applications**.
It analyzes an unoptimized e-commerce transaction processing and aggregation pipeline (`baseline_app.py`) that suffers from quadratic complexity ($O(N^2)$) and linear scans, profiles the execution using `cProfile` and `timeit`, and implements high-performance algorithmic optimizations in `optimized_app.py` delivering an **84.2x end-to-end speedup**.

---

## 2. Folder & File Structure

```
week4/
├── baseline_app.py          # Original unoptimized application with O(N^2) bottlenecks
├── optimized_app.py         # Refactored high-performance application with O(N) algorithms
├── profiler_benchmarks.py   # Benchmark harness executing cProfile and timeit suites
├── test_equivalence.py      # Automated equivalence unit tests (7 tests, 100% parity)
├── profiling_report.md      # Detailed performance report with call trees and diffs
├── WEEK4_FULL_SUBMISSION.md # Master consolidated submission document
├── package_deliverable.py   # Packaging automation script for ZIP creation
├── week4_deliverable.zip    # Final packaged self-contained submission archive
├── task.md                  # Week 4 internship task prompt
└── README.md                # Project user manual and execution guide
```

---

## 3. Summary of Identified Bottlenecks & Fixes

| Bottleneck # | Inefficient Function | Algorithmic Bottleneck | Optimization Applied |
|:---:|:---|:---|:---|
| **1** | `find_duplicate_orders` | $O(N^2)$ nested loop scanning | Replaced with $O(N)$ Hash Set (`seen_ids`, `duplicate_ids`) lookup. |
| **2** | `join_orders_with_customers` | $O(N \times M)$ linear list search | Pre-indexed customers into an $O(1)$ Hash Map dictionary. |
| **3** | `generate_audit_log` | In-loop `re.compile()` and $O(K^2)$ string `+` | Pre-compiled regex pattern at module level; built with list `"".join()`. |
| **4** | `calculate_tier_revenue` | Redundant two-pass nested accumulation | Streamlined accumulator using `defaultdict` and single-pass math. |

---

## 4. Quantitative Performance Comparison

| Component | Baseline Runtime | Optimized Runtime | Speedup | Algorithmic Complexity |
|:---|:---:|:---:|:---:|:---:|
| **Duplicate Detection** | `0.044616 s` | `0.000164 s` | **272.1x** | $O(N^2) \rightarrow O(N)$ |
| **Customer Join** | `0.019452 s` | `0.000753 s` | **25.8x** | $O(N \times M) \rightarrow O(N + M)$ |
| **String Logging & Regex** | `0.001183 s` | `0.000873 s` | **1.4x** | $O(K^2) \rightarrow O(K)$ |
| **FULL PIPELINE MACRO** | **1.610250 s** | **0.019129 s** | **84.2x** | **99.1% Total Time Reduction** |

---

## 5. How to Run Benchmarks, Profilers & Tests

### Step 1: Run the Profiling and Benchmarking Harness (cProfile + timeit)
```cmd
cmd /c cd week4 && python profiler_benchmarks.py
```

### Step 2: Run the Baseline Script
```cmd
cmd /c cd week4 && python baseline_app.py
```

### Step 3: Run the Optimized Script
```cmd
cmd /c cd week4 && python optimized_app.py
```

### Step 4: Run Functional Parity & Equivalence Tests
```cmd
cmd /c cd week4 && python -m unittest test_equivalence.py -v
```

### Step 5: Repackage Submission ZIP Archive
```cmd
cmd /c cd week4 && python package_deliverable.py
```

---

## 6. Full Evaluation Criteria Compliance Checklist (Items 1–18)

| Task.md Requirement | Implementation Details | Status |
|:---|:---|:---:|
| **Item 1–2: Performance optimization of Python application** | Developed transaction analytics pipeline with identifiable bottlenecks | [x] **Verified** |
| **Item 3–5: Self-contained ZIP archive deliverable** | `week4_deliverable.zip` created via `package_deliverable.py` | [x] **Verified** |
| **Item 6–7: Baseline performance analysis with profiling tools** | Profiled using `cProfile` and `pstats` (documented in report) | [x] **Verified** |
| **Item 8–9: Bottleneck identification and targeted segments** | Documented $O(N^2)$ duplicate check, linear join, string concatenation | [x] **Verified** |
| **Item 10–11: Implement optimizations (algorithmic, data structures)** | Hash sets, dictionary indexing, `str.join()`, pre-compiled regex | [x] **Verified** |
| **Item 12–13: Detailed report with before-and-after benchmarks** | Documented in `profiling_report.md` with 84.2x speedup | [x] **Verified** |
| **Item 14: Final verification of exact functionality & accuracy** | 7 automated equivalence unit tests passing in `test_equivalence.py` | [x] **Verified** |
| **Item 15–18: Rigor of analysis and self-contained delivery** | 100% Python Standard Library, zero external datasets needed | [x] **Verified** |

