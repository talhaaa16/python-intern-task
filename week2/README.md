# Week 2: Debugging and Troubleshooting Python Applications

A complete, practical debugging and troubleshooting suite demonstrating root-cause analysis, bug reproduction, code refactoring, and automated validation.

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Folder & File Structure](#folder--file-structure)
3. [Summary of Identified Bugs](#summary-of-identified-bugs)
4. [How to Run & Reproduce](#how-to-run--reproduce)
   - [Step 1: Reproduce Bugs in Legacy Script](#step-1-reproduce-bugs-in-legacy-script)
   - [Step 2: Run the Corrected Application](#step-2-run-the-corrected-application)
   - [Step 3: Run Automated Verification Tests](#step-3-run-automated-verification-tests)
5. [Deliverable Checklist](#deliverable-checklist)

---

## 1. Overview
This project satisfies all requirements for **Week 2 Task: Debugging and Troubleshooting Python Applications**. 
It takes an unstable legacy inventory and sales script (`faulty_app.py`), exposes its vulnerabilities, investigates root causes, and presents a fully corrected, hardened, and optimized production-ready version (`corrected_app.py`).

---

## 2. Folder & File Structure

```
week2/
├── sample_inventory.csv     # Sample CSV dataset for inventory processing
├── faulty_app.py            # Legacy script containing 8 real-world bugs
├── reproduce_bugs.py        # Automated reproduction suite demonstrating each bug
├── corrected_app.py         # Refactored, bug-free, and optimized application
├── test_debugging.py        # Automated unit tests validating all 8 bug fixes
├── debugging_log.md         # Comprehensive bug report with before/after diffs
├── WEEK2_FULL_SUBMISSION.md # Consolidated all-in-one submission document
├── package_deliverable.py   # Utility script to generate submission ZIP archive
├── week2_deliverable.zip    # Final packaged submission deliverable
├── task.md                  # Week 2 internship task prompt
└── README.md                # Project manual and execution instructions
```

---

## 3. Summary of Identified Bugs

| Bug # | Faulty Area | Issue & Fix |
|:---:|:---|:---|
| **1** | `__init__(self, inventory=[])` | **Mutable default argument**: Replaced with `None` default to prevent state leakage across instances. |
| **2** | `load_from_csv` | **Unhandled FileNotFoundError**: Added file existence checks and `try/except` blocks. |
| **3** | `display_inventory` | **Off-by-one loop error**: Switched to direct element iteration instead of `range(len + 1)`. |
| **4** | CSV data types | **String types**: Cast price to `float` and stock to `int` via `InventoryItem` dataclass. |
| **5** | `process_order` | **Discount calculation flaw**: Fixed mathematical order of operations and pricing formula. |
| **6** | `remove_out_of_stock_items` | **In-place list mutation**: Replaced with list comprehension to prevent skipping adjacent elements. |
| **7** | `calculate_average_price` | **ZeroDivisionError**: Added guard checking if matching items count is zero. |
| **8** | `export_sales_report` | **Bare except & leak**: Used `with open()` context manager and caught specific `(IOError, OSError)`. |

---

## 4. How to Run & Reproduce

### Step 1: Reproduce Bugs in Legacy Script
To see all the bugs trigger and display their exact exceptions and stack traces:
```cmd
cmd /c cd week2 && python reproduce_bugs.py
```

### Step 2: Run the Corrected Application
Launch the interactive, bug-free CLI inventory application:
```cmd
cmd /c cd week2 && python corrected_app.py
```

### Step 3: Run Automated Verification Tests
Run the unit test suite verifying that all bugs have been eliminated:
```cmd
cmd /c cd week2 && python test_debugging.py
```

### Step 4: Re-bundle Submission Archive
```cmd
cmd /c cd week2 && python package_deliverable.py
```

---

## 5. Deliverable Checklist
- [x] **Corrected Python script**: `corrected_app.py` is free from all bugs, with type hints and docstrings.
- [x] **Detailed debugging log**: `debugging_log.md` with hypotheses, tracebacks, before/after code diffs, and optimizations.
- [x] **Automated test suite**: `test_debugging.py` with 7 test cases covering all fixed scenarios.
- [x] **Submission ZIP archive**: `week2_deliverable.zip` created and ready for upload.
