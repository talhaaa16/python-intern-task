# Week 6: Integrating Continuous Integration (CI) in Python Projects
## Comprehensive Technical Report & CI Architecture Documentation

---

## 1. Executive Summary
Continuous Integration (CI) is an indispensable software engineering discipline wherein developers frequently merge code changes into a shared repository. Every push or pull request automatically triggers an automated pipeline that builds, lints, and tests the project to verify that regressions are intercepted before reaching production.

In Week 6 of the Python Internship Program, a fully automated, production-grade Continuous Integration pipeline was engineered for an Enterprise Order Processing and Analytics Service. The system incorporates:
1. **Automated Static Code Analysis & Linting**: Syntax parsing, PEP 8 enforcement, and public docstring compliance via an Abstract Syntax Tree (AST) engine (`src/linter.py`).
2. **Automated Unit & Integration Testing**: 17 comprehensive test cases (`tests/test_service.py`) testing domain models, calculations, state transitions, exceptions, and business summaries.
3. **Multi-Version Cross-Platform CI Workflow**: A GitHub Actions workflow configuration (`.github/workflows/ci.yml` and `ci_workflow.yml`) executing parallel test matrices across Python 3.9, 3.10, 3.11, 3.12, and 3.13 on both Ubuntu and Windows runner environments.
4. **Local CI Simulation Runner (`local_ci_runner.py`)**: A developer tool that mirrors the cloud CI pipeline locally, executing environment inspection, linting, test discovery, and automated report generation (`ci_build_report.json`).
5. **Strict Build Status Enforcement**: Any linting violation or test regression immediately triggers a non-zero exit code (`exit 1`), halting the pipeline and rejecting unverified commits.

---

## 2. CI Pipeline Architecture & Workflow

```
+-----------------------------------------------------------------------------------+
|                           Git Push / Pull Request Event                           |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|               GitHub Actions Workflow Matrix (Ubuntu & Windows Runners)           |
|                     Python 3.9 | 3.10 | 3.11 | 3.12 | 3.13                        |
+-----------------------------------------------------------------------------------+
                                         |
     +-----------------------------------+-----------------------------------+
     |                                   |                                   |
     v                                   v                                   v
[Stage 1: Setup]                [Stage 2: Linting]             [Stage 3: Automated Tests]
- actions/checkout@v4           - AST syntax tree parse        - Test discovery (unittest)
- actions/setup-python@v5       - PEP8 line length (<120)      - 17 unit & integration tests
- Runtime introspection         - Docstring presence check     - Boundary & error tests
                                - Trailing whitespace guard    - Strict fail on error
                                         |
                                         v
                      +--------------------------------------+
                      |    [Stage 4: Build Report & Artifact] |
                      |    - Generate ci_build_report.json   |
                      |    - Upload build artifacts to GitHub|
                      +--------------------------------------+
```

---

## 3. Detailed CI Pipeline Configuration

The remote CI pipeline is configured using GitHub Actions (`.github/workflows/ci.yml`):
- **Triggers**: Executed on every `push` and `pull_request` targeting `master` or `main`, with `workflow_dispatch` enabled for manual runs.
- **Strategy Matrix**: Tests across both `ubuntu-latest` and `windows-latest` operating systems, evaluating Python versions `3.9`, `3.10`, `3.11`, `3.12`, and `3.13`.
- **Fail-Fast Setting**: Configured as `fail-fast: false` to ensure full matrix visibility across all platforms even if one runtime encounters an issue.
- **Artifact Archiving**: `actions/upload-artifact@v4` automatically captures `ci_build_report.json` for auditability.

---

## 4. Local CI Runner Simulation (`local_ci_runner.py`)

To streamline developer velocity and eliminate the wait time of pushing to remote repositories, `local_ci_runner.py` replicates the CI pipeline locally:
- **Stage 1 (Environment Validation)**: Verifies Python runtime satisfies the `>= 3.9` threshold.
- **Stage 2 (Static Linting)**: Analyzes `src/` and `tests/` using `ProjectLinter`.
- **Stage 3 (Test Execution)**: Executes `unittest.TestLoader.discover()` with verbose reporting.
- **Stage 4 (Coverage Estimation)**: Computes lines of code (LOC) and test assertion coverage (>95%).
- **Stage 5 (Report Serialization)**: Emits `ci_build_report.json` containing timestamps, platform specs, and stage results.

### Local Execution Command
```bash
python week6/local_ci_runner.py
```

---

## 5. Challenges Encountered & Technical Resolutions

| Challenge ID | Symptom / Issue | Root Cause | Engineering Resolution |
| :--- | :--- | :--- | :--- |
| **CHG-01** | Python 3.13 `DeprecationWarning` | `datetime.utcnow()` is deprecated in Python 3.12+ | Replaced `datetime.utcnow()` with timezone-aware `datetime.now(timezone.utc).isoformat()`. |
| **CHG-02** | Cross-Platform Shell Argument Escaping | Shell quotes (`\"test_*.py\"`) parsed differently on Windows `cmd` vs Linux `bash` | Used standard clean flags in `unittest discover -s tests -v` without escaped quotation wrappers. |
| **CHG-03** | Missing Docstring Violations | `ProjectLinter` detected missing class and method docstrings | Refactored all public classes, helper functions, and domain properties to include standard PEP 257 docstrings. |
| **CHG-04** | Line Length & Whitespace Inconsistencies | Line length exceeded 120 characters in `core_service.py` | Wrapped method signatures and multiline calls to adhere to standard 120-character width limits. |
| **CHG-05** | Pipeline Isolation & Self-Containment | Need for completely reproducible tests without external dependencies | Built an AST-based linter and unittest suite utilizing 100% Python Standard Library modules (`ast`, `unittest`, `dataclasses`, `json`). |

---

## 6. Test Suite & Coverage Verification

The automated test suite (`tests/test_service.py`) contains 17 test cases:
1. `test_valid_customer_creation`: Verifies customer registration with valid tiers.
2. `test_invalid_email_format`: Asserts rejection of malformed email strings.
3. `test_invalid_customer_tier`: Confirms unknown tier strings raise `ValueError`.
4. `test_order_item_total_calculation`: Verifies line item math (`price * quantity`).
5. `test_negative_unit_price`: Asserts negative prices raise `ValueError`.
6. `test_zero_or_negative_quantity`: Asserts zero/negative quantities raise `ValueError`.
7. `test_order_financial_computations_without_discount`: Validates subtotal, 5% tax, and grand total.
8. `test_order_financial_computations_with_discount`: Validates 10% discount, taxable base, and grand total.
9. `test_invalid_discount_range`: Asserts out-of-bounds discount percentages raise `ValueError`.
10. `test_duplicate_customer_registration_fails`: Verifies duplicate customer IDs are rejected.
11. `test_create_order_for_unknown_customer_fails`: Asserts missing customer raises `KeyError`.
12. `test_create_order_empty_items_fails`: Asserts empty order items raise `ValueError`.
13. `test_automatic_tier_discount_application`: Verifies tier discounts are automatically applied.
14. `test_successful_order_processing`: Validates end-to-end PENDING to COMPLETED lifecycle.
15. `test_process_non_pending_order_fails`: Asserts invalid status transitions raise `RuntimeError`.
16. `test_order_cancellation`: Verifies pending order cancellation and locks completed orders.
17. `test_compute_summary_analytics`: Verifies cumulative revenue, taxes, and average order value.

---

## 7. Instructions for Replicating Environment

1. **Prerequisites**: Python 3.9, 3.10, 3.11, 3.12, or 3.13 installed.
2. **Clone / Extract Project**:
   ```bash
   cd week6
   ```
3. **Execute Local CI Pipeline**:
   ```bash
   python local_ci_runner.py
   ```
4. **Run Test Suite Directly**:
   ```bash
   python -m unittest discover -s tests -v
   ```
5. **Run AST Linter Directly**:
   ```bash
   python src/linter.py
   ```
6. **Package Submission Archive**:
   ```bash
   python package_deliverable.py
   ```

