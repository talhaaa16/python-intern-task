# Week 3: Automated Testing for Python Applications
## Finance Analysis Module - Comprehensive Test Suite Documentation & TDD Report

---

## 1. Executive Summary & Objective

The objective of Week 3 is to design, develop, and thoroughly validate a moderately complex, production-ready Python module using **Test-Driven Development (TDD)** and automated testing methodologies (`unittest`).

The chosen domain is an enterprise **Finance Analysis & Transaction Analytics Module** (`module_logic.py`, `models.py`), providing:
- Strongly typed, immutable transaction records (`CREDIT`, `DEBIT`).
- Balance calculation with floating-point rounding safeguards.
- Categorized spending breakdowns and multi-field conditional querying.
- Savings rate calculation and comprehensive `AccountSummary` analytics.
- Transaction batch ingestion with atomic rollback on failure.
- CSV serialization export.

A total of **31 automated test cases** were designed and implemented in `test_suite.py`, covering unit tests, edge cases, boundary conditions, floating-point precision, error handling, and end-to-end integration workflows.

---

## 2. Testing Methodology: Test-Driven Development (TDD) Workflow

The project strictly adhered to the canonical **Red-Green-Refactor** TDD cycle:

```
      +-------------------------------------------------------+
      |  1. RED: Write a failing unit test for a requirement  |
      +-------------------------------------------------------+
                                  |
                                  v
      +-------------------------------------------------------+
      | 2. GREEN: Write minimum functional code to make test  |
      |           pass cleanly without error                  |
      +-------------------------------------------------------+
                                  |
                                  v
      +-------------------------------------------------------+
      | 3. REFACTOR: Clean code, optimize data structures,    |
      |              enforce type hints, verify all tests pass|
      +-------------------------------------------------------+
```

### Concrete TDD Examples in Development:

#### Concrete Example 1: Non-Positive Amount Boundary Validation
- **Requirement**: Financial transactions cannot have zero or negative amounts.
- **RED (Phase 1)**: Wrote `test_tc04_amount_zero_rejected` and `test_tc05_negative_amount_rejected`.
  ```python
  def test_tc04_amount_zero_rejected(self):
      with self.assertRaises(ValueError):
          Transaction("TX-104", 0.00, TransactionType.CREDIT)
  ```
  *Result*: Test failed with `AssertionError: ValueError not raised` because initial dataclass accepted any numeric amount.
- **GREEN (Phase 2)**: Added validation inside `__post_init__` of `models.py`:
  ```python
  if self.amount <= 0:
      raise ValueError(f"Transaction amount must be strictly greater than zero. Received: {self.amount}")
  ```
  *Result*: Test passed immediately (`OK`).
- **REFACTOR (Phase 3)**: Added type verification (`isinstance(self.amount, (int, float))`) to reject string amounts before comparing values, raising `TypeError` for non-numerics.

#### Concrete Example 2: Floating-Point Precision Rounding
- **Requirement**: Multiple monetary additions must not suffer from IEEE 754 floating-point inaccuracies (e.g., `0.10 + 0.20 = 0.30000000000000004`).
- **RED (Phase 1)**: Wrote `test_tc17_floating_point_precision_rounding`.
  ```python
  self.analyzer.add_transaction(Transaction("T1", 0.10, TransactionType.CREDIT))
  self.analyzer.add_transaction(Transaction("T2", 0.20, TransactionType.CREDIT))
  self.assertEqual(self.analyzer.calculate_balance(), 0.30)
  ```
  *Result*: Failed when balance returned raw unrounded float `0.30000000000000004`.
- **GREEN (Phase 2)**: Enforced `round(balance, 2)` across all financial return values.
  *Result*: Test passed (`0.30 == 0.30`).
- **REFACTOR (Phase 3)**: Centralized rounding logic into property getters (`get_total_credits`, `get_total_debits`, `calculate_balance`).

#### Concrete Example 3: Atomic Batch Ingestion with Rollback
- **Requirement**: When adding a batch of transactions, if any transaction causes an error (such as a duplicate ID), no transactions from that batch should remain in the ledger.
- **RED (Phase 1)**: Wrote `test_tc29_batch_ingestion_rollback_on_failure`.
  *Result*: Failed because partial additions remained in `_transactions`.
- **GREEN (Phase 2)**: Implemented state snapshotting in `add_batch()`:
  ```python
  backup = list(self._transactions)
  try:
      for tx in transactions:
          self.add_transaction(tx)
  except Exception as exc:
      self._transactions = backup
      raise exc
  ```
  *Result*: Test passed.

---

## 3. Comprehensive Test Case Matrix (31 Automated Test Cases)

| Test ID | Test Category | Scenario Description | Input Data | Expected Outcome | Verification Status |
|---|---|---|---|---|:---:|
| **TC-01** | Unit (Model) | Valid CREDIT transaction creation | Amount: `2500.50`, Type: `CREDIT` | Attributes correctly populated | **PASS** |
| **TC-02** | Unit (Model) | Valid DEBIT transaction creation | Amount: `85.25`, Type: `DEBIT` | Attributes correctly populated | **PASS** |
| **TC-03** | Unit (Model) | String type coercion & whitespace trim | Type string: `" DEBIT "` | Coerced to `TransactionType.DEBIT` | **PASS** |
| **TC-04** | Edge Case | Zero amount boundary condition | Amount: `0.00` | `ValueError` raised | **PASS** |
| **TC-05** | Edge Case | Negative amount input | Amount: `-500.00` | `ValueError` raised | **PASS** |
| **TC-06** | Error Handling | Non-numeric amount type mismatch | Amount: `"100.00"` (str) | `TypeError` raised | **PASS** |
| **TC-07** | Error Handling | Blank/whitespace transaction ID | ID: `""` or `"   "` | `ValueError` raised | **PASS** |
| **TC-08** | Error Handling | Unsupported transaction type string | Type: `"TRANSFER"` | `ValueError` raised | **PASS** |
| **TC-09** | Unit (Model) | Empty category fallback | Category: `""` | Defaults to `"Other"` | **PASS** |
| **TC-10** | Serialization | Transaction `to_dict` structure | Valid Transaction | Complete dictionary output | **PASS** |
| **TC-11** | Boundary | Initial analyzer state | No transactions | Count: 0, Balance: 0.00 | **PASS** |
| **TC-12** | Unit (Logic) | Ingest single valid transaction | 1 CREDIT Transaction | Ingested successfully | **PASS** |
| **TC-13** | Error Handling | Ingest incompatible non-Transaction object | Input: `{"amount": 100}` | `TypeError` raised | **PASS** |
| **TC-14** | Error Handling | Ingest duplicate transaction ID | Ingest ID `"DUP-01"` twice | `ValueError` raised on 2nd ingest | **PASS** |
| **TC-15** | Unit (Logic) | Balance calculation with credits only | Credits: `1200.50`, `300.25` | Balance = `1500.75` | **PASS** |
| **TC-16** | Unit (Logic) | Balance calculation with debits only | Debits: `45.00`, `55.50` | Balance = `-100.50` | **PASS** |
| **TC-17** | Precision | Floating point addition rounding | Credits: `0.10`, `0.20` | Balance = `0.30` | **PASS** |
| **TC-18** | Unit (Logic) | Spending categorized by DEBIT only | Debits: Food `$155.50`, Utilities `$75.00` | Correct breakdown, credits excluded | **PASS** |
| **TC-19** | Boundary | Category totals when zero debits exist | Credits only | Empty dictionary `{}` | **PASS** |
| **TC-20** | Unit (Query) | Multi-filter by TransactionType | Ingest mixed list | Exact subset returned | **PASS** |
| **TC-21** | Unit (Query) | Multi-filter by category (case-insensitive) | Query: `"TRAVEL"`, Items: `"travel"` | 2 matching records returned | **PASS** |
| **TC-22** | Unit (Query) | Multi-filter by amount range | Min: `20.0`, Max: `100.0` | Matching records returned | **PASS** |
| **TC-23** | Error Handling | Filter with inverted range | Min: `100.0`, Max: `50.0` | `ValueError` raised | **PASS** |
| **TC-24** | Unit (Logic) | Identify single largest debit expense | Debits: `$45`, `$1200`, `$250` | Identifies `$1200` record | **PASS** |
| **TC-25** | Boundary | Largest expense with zero debits | Credits only | Returns `None` without crashing | **PASS** |
| **TC-26** | Unit (Logic) | Personal savings rate calculation | Credits: `4000`, Debits: `1000` | Savings rate = `75.0%` | **PASS** |
| **TC-27** | Boundary | Savings rate calculation with 0 income | Debits only | Returns `0.0%` without `ZeroDivisionError` | **PASS** |
| **TC-28** | Integration | Batch ingestion atomic success | Batch of 3 transactions | All 3 added, balance updated | **PASS** |
| **TC-29** | Integration | Batch ingestion failure rollback | Batch containing duplicate ID | Reverts ledger to previous state | **PASS** |
| **TC-30** | Integration | Full `AccountSummary` snapshot | Multi-category mixed transactions | All metrics aggregated correctly | **PASS** |
| **TC-31** | Integration | CSV report export format | Ingested transactions | Valid CSV string with headers | **PASS** |

---

## 4. Test Execution Instructions & Output

### Running the Test Suite
The test suite utilizes Python's native `unittest` framework:

```cmd
cmd /c cd week3 && python -m unittest test_suite.py -v
```

### Execution Output:
```text
test_tc28_batch_ingestion_atomic_success ... ok
test_tc29_batch_ingestion_rollback_on_failure ... ok
test_tc30_generate_summary_integration ... ok
test_tc31_export_csv_roundtrip_integration ... ok
test_tc11_initial_state_empty ... ok
test_tc12_add_transaction_success ... ok
test_tc13_add_non_transaction_type_error ... ok
test_tc14_duplicate_transaction_id_rejected ... ok
test_tc15_calculate_balance_credits_only ... ok
test_tc16_calculate_balance_debits_only ... ok
test_tc17_floating_point_precision_rounding ... ok
test_tc18_category_totals_debits_only ... ok
test_tc19_category_totals_empty_when_no_debits ... ok
test_tc20_filter_by_type ... ok
test_tc21_filter_by_category_case_insensitive ... ok
test_tc22_filter_by_amount_range ... ok
test_tc23_filter_invalid_amount_range_raises_error ... ok
test_tc24_get_largest_expense ... ok
test_tc25_get_largest_expense_none_when_no_debits ... ok
test_tc26_calculate_savings_rate ... ok
test_tc27_savings_rate_zero_when_no_income ... ok
test_tc01_valid_credit_transaction ... ok
test_tc02_valid_debit_transaction ... ok
test_tc03_string_type_coercion_and_normalization ... ok
test_tc04_amount_zero_rejected ... ok
test_tc05_negative_amount_rejected ... ok
test_tc06_non_numeric_amount_rejected ... ok
test_tc07_empty_transaction_id_rejected ... ok
test_tc08_invalid_transaction_type_string_rejected ... ok
test_tc09_default_category_fallback ... ok
test_tc10_transaction_to_dict_serialization ... ok

----------------------------------------------------------------------
Ran 31 tests in 0.003s

OK
```

---

## 5. Code Review & Refactoring Log (Steps 10–11)

Following test verification, the codebase was reviewed and refactored for clarity and maintainability:

1. **Defensive Copies**:
   - Replaced direct access to `self.transactions` list with a property getter returning `list(self._transactions)`. This prevents callers from mutating the internal transaction list bypassing validation.
2. **Encapsulation & Type Hints**:
   - Added complete PEP 484 type annotations (`List[Transaction]`, `Optional[Transaction]`, `Dict[str, float]`) across all functions.
3. **Decoupled Analytics**:
   - Split complex reporting into atomic single-responsibility methods (`get_total_credits()`, `get_total_debits()`, `get_largest_expense()`, `calculate_savings_rate()`).
4. **Resilient Aggregation**:
   - Handled division by zero across savings rate and average transaction computations.

---

## 6. Full Evaluation Criteria Compliance Checklist

| Item # | Evaluation Requirement from Task.md | Implementation Details | Verification Status |
|:---:|:---|:---|:---:|
| **1–2** | Moderately complex Python module with TDD practices | `FinanceAnalyzer` in `module_logic.py` and dataclasses in `models.py` | [x] **Fulfilled** |
| **3** | Self-contained ZIP archive with code, tests, and documentation | `week3_deliverable.zip` generated via `package_deliverable.py` | [x] **Fulfilled** |
| **4–5** | Clean module design structured for testability | Decoupled architecture, pure functions, deterministic outputs | [x] **Fulfilled** |
| **6–7** | Comprehensive test suite covering edge cases and TDD demonstration | 31 automated tests covering negative values, zeros, duplicates, precision | [x] **Fulfilled** |
| **8–9** | Detailed documentation explaining test coverage & how to run | Documented in `test_documentation.md` and `README.md` | [x] **Fulfilled** |
| **10–11** | Review and refactor code for maintainability without breaking tests | Refactored with defensive copies, property getters, and type annotations | [x] **Fulfilled** |
| **12** | Validate tests run in clean environment | Native standard library, zero external pip packages needed | [x] **Fulfilled** |
| **13–15** | Evaluation criteria adherence & self-contained deliverable | Complete test matrix, TDD examples, and packaged ZIP archive | [x] **Fulfilled** |
