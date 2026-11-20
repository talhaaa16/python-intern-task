# Python Internship Program — Comprehensive Portfolio & Deliverables
## Yuva Internship Program (Weeks 1 – 6)

Welcome to the master repository for the Python Internship Program. This repository contains the complete source code, automated test suites, profiling benchmarks, cybersecurity hardening implementations, CI/CD pipelines, and technical documentation developed across all six weeks of the program.

---

## 📋 Curriculum & Weekly Project Index

| Week | Project Focus | Core Architectural Highlights | Key Deliverables & Reports |
|:---:|:---|:---|:---|
| **[Week 1](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/README.md)** | **Object-Oriented Programming (OOP) & CLI Architecture** | Layered design (CLI, Manager, Storage, Models), task serialization, priority filters, and input validation. | • [week1/README.md](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/README.md)<br>• [architecture_plan.md](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/architecture_plan.md)<br>• `test_todo.py` (Unit tests) |
| **[Week 2](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week2/README.md)** | **Debugging, Troubleshooting & Code Refactoring** | Diagnosis of 8 critical bugs (mutable defaults, off-by-one errors, resource leaks, type coercion), bug reproduction suite. | • [week2/README.md](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week2/README.md)<br>• [debugging_log.md](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week2/debugging_log.md)<br>• `reproduce_bugs.py` & `corrected_app.py` |
| **[Week 3](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week3/README.md)** | **Automated Testing & Test-Driven Development (TDD)** | 31 automated unit and integration tests, Red-Green-Refactor case studies, boundary edge cases, and 100% test passing rate. | • [week3/README.md](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week3/README.md)<br>• [test_documentation.md](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week3/test_documentation.md)<br>• `test_suite.py` (31 tests) |
| **[Week 4](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week4/README.md)** | **Performance Analysis & Algorithmic Optimization** | Bottleneck detection via `cProfile` and `timeit`, transforming O(N^2) nested loops into O(1) hash lookups, achieving an **84.2x speedup**. | • [week4/README.md](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week4/README.md)<br>• [profiling_report.md](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week4/profiling_report.md)<br>• `profiler_benchmarks.py` & `test_equivalence.py` |
| **[Week 5](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week5/README.md)** | **Cybersecurity & Application Hardening** | Remediation of 8 OWASP Top 10 vulnerabilities (SQLi, Command Injection, Path Traversal), PBKDF2 hashing, AES PII encryption. | • [week5/README.md](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week5/README.md)<br>• [security_audit_report.md](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week5/security_audit_report.md)<br>• `simulate_attacks.py` & `test_security.py` |
| **[Week 6](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week6/README.md)** | **Continuous Integration (CI) in Python Projects** | GitHub Actions multi-version matrix (Python 3.9–3.13 on Ubuntu/Windows), AST static linter, local CI runner, and automated build artifact generation. | • [week6/README.md](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week6/README.md)<br>• [WEEK6_FULL_SUBMISSION.md](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week6/WEEK6_FULL_SUBMISSION.md)<br>• `local_ci_runner.py` & `ci_workflow.yml` |

---

## 🛠️ Global Standards & Engineering Principles
Across all weekly modules, the following engineering standards were strictly adhered to:
1. **Zero External Dependencies**: All core logic, testing suites, encryption modules, and CI runners rely exclusively on the **Python Standard Library** (`dataclasses`, `unittest`, `hashlib`, `ast`, `json`, `cProfile`, `timeit`).
2. **Cross-Platform Compatibility**: Fully validated on Windows and Linux runtimes across modern Python versions (3.9+ through 3.13).
3. **Automated Verification**: Every project is accompanied by dedicated automated test suites enforcing functional equivalence, security boundaries, or performance metrics.
4. **Self-Contained Deliverables**: Each week includes an automated packaging script (`package_deliverable.py`) that generates a standalone `.zip` archive containing all relevant source files and reports.

---

## 🚀 How to Navigate and Run Any Module

To run any individual module or test suite, navigate to its respective directory:

```bash
# Week 1: Run To-Do List Application
cd week1 && python main.py

# Week 2: Run Bug Reproduction & Corrected App
cd week2 && python reproduce_bugs.py
cd week2 && python corrected_app.py

# Week 3: Run Full TDD Test Suite (31 tests)
cd week3 && python test_suite.py

# Week 4: Run Performance Profiling Benchmarks
cd week4 && python profiler_benchmarks.py

# Week 5: Run Penetration Testing Simulations
cd week5 && python simulate_attacks.py

# Week 6: Run Local Continuous Integration Pipeline
cd week6 && python local_ci_runner.py
```

