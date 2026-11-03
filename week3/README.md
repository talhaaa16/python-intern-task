# Week 3: Automated Testing - Finance Analysis Module

A professional, enterprise-grade Finance Analysis module built using **Test-Driven Development (TDD)** practices, supported by a comprehensive automated test suite of **31 test cases** and thorough documentation.

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Folder & File Structure](#folder--file-structure)
3. [Core Module Features](#core-module-features)
4. [TDD Methodology & Concrete Examples](#tdd-methodology--concrete-examples)
5. [Automated Test Suite (31 Tests)](#automated-test-suite-31-tests)
6. [How to Run Tests & Package Deliverable](#how-to-run-tests--package-deliverable)
7. [Full Evaluation Criteria Checklist (Items 1–16)](#full-evaluation-criteria-checklist-items-116)

---

## 1. Project Overview
This project satisfies all requirements for **Week 3 Task: Writing Automated Tests for Python Applications**.
It introduces a moderately complex, modular financial analysis library (`FinanceAnalyzer` and `Transaction` models) and a complete `unittest` test suite verifying arithmetic precision, boundary edge cases, multi-conditional filtering, and transactional batch rollbacks.

---

## 2. Folder & File Structure

```
week3/
├── models.py               # Domain entities (Transaction, TransactionType, AccountSummary)
├── module_logic.py         # Business logic engine (FinanceAnalyzer)
├── test_suite.py           # Automated test suite (31 unit & integration tests)
├── test_documentation.md   # Comprehensive test methodology and TDD report
├── WEEK3_FULL_SUBMISSION.md# Master consolidated submission documentation
├── package_deliverable.py  # Automation script for ZIP packaging
├── week3_deliverable.zip   # Final self-contained submission archive
├── task.md                 # Week 3 internship task prompt
└── README.md               # User manual and execution guide
```

---

## 3. Core Module Features
- **Strict Data Integrity**: Validation on transaction ID, positive amounts, and standardized enum types (`CREDIT`, `DEBIT`).
- **Precision Financial Math**: Accurate net balance calculation with automatic 2-decimal rounding preventing float drift.
- **Categorized Spending Breakdown**: Aggregates debit expenses across categories (Food, Rent, Utilities, etc.).
- **Multi-Conditional Ledger Filtering**: Filter by type, category, or amount ranges.
- **Transactional Batch Ingestion**: Adds transaction batches atomically with rollback safeguards.
- **Summary & Analytics**: Computes personal savings rate, largest debit expense, average transaction value, and exports to CSV.

---

## 4. TDD Methodology & Concrete Examples

The module was developed strictly following the **Red-Green-Refactor** development cycle:

1. **Concrete Example 1: Boundary Condition (Non-Positive Amounts)**
   - *RED*: Wrote `test_tc04_amount_zero_rejected` and `test_tc05_negative_amount_rejected`. Tests failed as dataclass initially accepted any float.
   - *GREEN*: Added validation inside `__post_init__` of `Transaction` in `models.py` raising `ValueError` when `amount <= 0`.
   - *REFACTOR*: Added `isinstance(self.amount, (int, float))` type checking to prevent comparing strings against zero.

2. **Concrete Example 2: Floating Point Precision Drift**
   - *RED*: Wrote `test_tc17_floating_point_precision_rounding` checking `0.10 + 0.20 == 0.30`. Test failed returning `0.30000000000000004`.
   - *GREEN*: Applied `round(balance, 2)` across balance and aggregate functions.
   - *REFACTOR*: Standardized rounding in `to_dict` and model serialization.

3. **Concrete Example 3: Atomic Batch Rollback**
   - *RED*: Wrote `test_tc29_batch_ingestion_rollback_on_failure` expecting atomic rollback if duplicate ID is encountered. Failed on partial insertion.
   - *GREEN*: Implemented snapshot state backup in `add_batch` restoring ledger on exception.
   - *REFACTOR*: Cleaned exception bubbling and memory copies.

---

## 5. Automated Test Suite (31 Tests)

The test suite in `test_suite.py` includes **31 test cases** divided into 3 focused test classes:

| Class | Coverage | Tests |
|---|---|:---:|
| **`TestTransactionModel`** | Dataclass validation, types, zero/negative guards, serialization | 10 Tests (`TC-01` to `TC-10`) |
| **`TestFinanceAnalyzerUnit`** | Ingestion, balance, precision, categories, filtering, analytics | 17 Tests (`TC-11` to `TC-27`) |
| **`TestFinanceAnalyzerIntegration`** | Batch transactions, rollback, summary snapshot, CSV export | 4 Tests (`TC-28` to `TC-31`) |

---

## 6. How to Run Tests & Package Deliverable

### Run the Automated Test Suite (Verbose Mode):
```cmd
cmd /c cd week3 && python -m unittest test_suite.py -v
```

### Run All Tests Directly:
```cmd
cmd /c cd week3 && python test_suite.py
```

### Re-package the Submission ZIP Archive:
```cmd
cmd /c cd week3 && python package_deliverable.py
```

---

## 7. Full Evaluation Criteria Checklist (Items 1–16)

| Task.md Requirement | Implementation Details | Status |
|:---|:---|:---:|
| **Item 1–2**: Moderately complex module with automated tests & TDD | `FinanceAnalyzer` in `module_logic.py` and models in `models.py` | [x] **Verified** |
| **Item 3**: Self-contained ZIP archive with module, tests, and documentation | `week3_deliverable.zip` created containing all code and docs | [x] **Verified** |
| **Item 4–5**: Module structured for easy testability | Decoupled architecture, pure functions, deterministic outputs | [x] **Verified** |
| **Item 6–7**: Comprehensive test suite covering edge cases and TDD methodology | 31 automated tests covering edge cases, zeros, negative values, rollbacks | [x] **Verified** |
| **Item 8–9**: Detailed test documentation explaining coverage and execution | Full test matrix and how-to-run instructions in `test_documentation.md` | [x] **Verified** |
| **Item 10–11**: Code review and refactoring log ensuring test preservation | Documented in Section 5 of `test_documentation.md` | [x] **Verified** |
| **Item 12**: Verification in a clean environment | 100% Python Standard Library, zero external pip dependencies | [x] **Verified** |
| **Item 13–16**: Adherence to evaluation criteria and self-contained delivery | Complete package verified and ready for evaluation | [x] **Verified** |
