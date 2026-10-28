# Week 2: Debugging and Troubleshooting Report
## Comprehensive Analysis, Root-Cause Investigation, and Resolution Log

---

## 1. Executive Summary
This document fulfills the requirements for **Week 2: Debugging and Troubleshooting Python Applications**. 
A legacy script (`faulty_app.py`) simulating an enterprise Inventory and Sales Management System was subjected to systematic code review, reproduction testing, debugger tracing (`pdb`), and refactoring.

A total of **8 critical bugs and design deficiencies** were identified across file I/O operations, loop control boundaries, mutable defaults, type conversions, and exception handling. All issues were reproduced, isolated, resolved in `corrected_app.py`, and verified using an automated unit test suite (`test_debugging.py`).

---

## 2. Bug Classification & Summary Matrix

| Bug ID | Component | Error Type / Symptom | Root Cause | Severity | Status |
|:---:|:---|:---|:---|:---:|:---:|
| **BUG-01** | `__init__` | State leakage across instances | Mutable default argument `inventory=[]` | **High** | **Resolved** |
| **BUG-02** | `load_from_csv` | Unhandled crash on missing file; resource leak | Missing `with` statement and no `try/except FileNotFoundError` | **High** | **Resolved** |
| **BUG-03** | `display_inventory` | `IndexError: list index out of range` | Off-by-one loop boundary `range(len(self.inventory) + 1)` | **Critical** | **Resolved** |
| **BUG-04** | `load_from_csv` / `process_order` | `TypeError` in arithmetic operations | Storing numeric prices and stock as raw strings from CSV | **Critical** | **Resolved** |
| **BUG-05** | `process_order` | Inaccurate order total calculation | Order of operations and string multiplication logic flaw | **High** | **Resolved** |
| **BUG-06** | `remove_out_of_stock_items` | Items skipped during deletion | In-place list mutation during forward `for item in self.inventory` loop | **Medium** | **Resolved** |
| **BUG-07** | `calculate_average_price` | `ZeroDivisionError: float division by zero` | Division by `count` without checking if `count == 0` | **High** | **Resolved** |
| **BUG-08** | `export_sales_report` | Silent failures & resource leaks | Bare `except:` clause masking errors; unclosed file descriptor | **Medium** | **Resolved** |

---

## 3. Detailed Bug-by-Bug Troubleshooting Logs

### BUG-01: Mutable Default Argument in Constructor

#### Description & Symptoms
When instantiating multiple `InventoryManager` objects without passing an initial inventory, items added to one instance unexpectedly appeared in subsequently created instances.

#### Hypothesis & Root Cause Analysis
In Python, default argument expressions in function definitions are evaluated **once** when the function definition is executed, not at call time. Therefore, `inventory=[]` creates a single shared list object across all instances using the default.

#### Debugging Trace
```python
# Using python interactive shell / pdb:
mgr1 = InventoryManager()
mgr1.inventory.append({"id": "999"})
mgr2 = InventoryManager()
print(id(mgr1.inventory) == id(mgr2.inventory))  # Evaluated to True!
```

#### Code Fix: Before vs. After
```diff
--- faulty_app.py
+++ corrected_app.py
@@ -10,3 +10,4 @@
-    def __init__(self, inventory=[]):
-        self.inventory = inventory
+    def __init__(self, inventory: Optional[List[InventoryItem]] = None):
+        self.inventory = list(inventory) if inventory is not None else []
```

---

### BUG-02: Resource Leak and Unhandled FileNotFoundError in File Loading

#### Description & Symptoms
Running `manager.load_from_csv("missing_file.csv")` immediately crashed the program with an unhandled `FileNotFoundError`. Furthermore, `open()` was called without a `with` block or explicit `close()`, leaving open file handles.

#### Root Cause
Missing file existence check and lack of context manager pattern.

#### Code Fix: Before vs. After
```diff
--- faulty_app.py
+++ corrected_app.py
-    def load_from_csv(self, filename="sample_inventory.csv"):
-        file = open(filename, "r")
-        reader = csv.reader(file)
+    def load_from_csv(self, filename: str = "sample_inventory.csv") -> bool:
+        if not os.path.exists(filename):
+            print(f"[Error] Inventory file '{filename}' not found.")
+            return False
+        try:
+            with open(filename, mode="r", encoding="utf-8") as file:
+                reader = csv.DictReader(file)
+                # parse lines...
+                return True
+        except (IOError, OSError) as err:
+            print(f"[Error] Failed to read inventory file: {err}")
+            return False
```

---

### BUG-03: Off-By-One Boundary Loop Error

#### Description & Symptoms
Calling `display_inventory()` with $N$ items crashed on the final iteration with:
```
IndexError: list index out of range
```

#### Root Cause
The loop header was written as `for i in range(len(self.inventory) + 1):`. Because Python lists are 0-indexed, indices run from `0` to `len - 1`. The `+ 1` forced an access at index `len`, which does not exist.

#### Code Fix: Before vs. After
```diff
--- faulty_app.py
+++ corrected_app.py
-        for i in range(len(self.inventory) + 1):
-            item = self.inventory[i]
+        for item in self.inventory:
+            print(f"[{item.id}] {item.name} - ${item.price:.2f}")
```

---

### BUG-04 & BUG-05: String Type Coercion & Discount Calculation Flaw

#### Description & Symptoms
When placing an order with quantity 2 and price `25.99`, string repetition occurred or `TypeError: unsupported operand type(s)` was raised. Stock comparison `target["stock"] < quantity` performed lexicographical string comparison rather than numerical comparison (e.g., `'9' > '100'`).

#### Root Cause
`csv.reader` returns raw string values. The application directly placed those strings into dictionaries without type coercion to `float` or `int`.

#### Code Fix: Before vs. After
```diff
--- faulty_app.py
+++ corrected_app.py
-            item = {
-                "price": row[3],
-                "stock": row[4]
-            }
-        raw_price = target["price"] * quantity
-        final_price = raw_price - raw_price * discount_pct / 100
+        # Using typed InventoryItem factory:
+        price = round(float(data["price"]), 2)
+        stock = int(data["stock"])
+
+        # Arithmetic calculation:
+        subtotal = target.price * quantity
+        discount_amount = subtotal * (discount_pct / 100.0)
+        final_price = round(subtotal - discount_amount, 2)
```

---

### BUG-06: Mutating a List While Iterating Over It

#### Description & Symptoms
When `remove_out_of_stock_items()` was executed on an inventory containing two consecutive out-of-stock items, the second item was skipped and remained in inventory.

#### Root Cause
In Python, iterating over a list using an internal index counter while calling `list.remove()` shifts all subsequent elements to the left by one position. The loop iterator advances to the next index, inadvertently bypassing the newly shifted adjacent element.

#### Code Fix: Before vs. After
```diff
--- faulty_app.py
+++ corrected_app.py
-        for item in self.inventory:
-            if int(item["stock"]) <= 0:
-                self.inventory.remove(item)
+        # Non-mutating list comprehension:
+        self.inventory = [item for item in self.inventory if item.stock > 0]
```

---

### BUG-07: Unchecked ZeroDivisionError

#### Description & Symptoms
Calling `calculate_average_price("NonExistentCategory")` or calling it on an empty inventory raised:
```
ZeroDivisionError: float division by zero
```

#### Root Cause
Calculation divided by `count` unconditionally without checking `if count == 0`.

#### Code Fix: Before vs. After
```diff
--- faulty_app.py
+++ corrected_app.py
-        return total / count
+        if not matching_items:
+            return 0.0
+        return round(sum(item.price for item in matching_items) / len(matching_items), 2)
```

---

### BUG-08: Bare Exception Handling and File Descriptor Leak

#### Description & Symptoms
`export_sales_report` utilized `except:` without specifying an exception class, silently masking errors and intercepting `KeyboardInterrupt` / `SystemExit`. Files were not closed safely upon error.

#### Root Cause
Antipattern of using bare `except:`, and lack of `with open(...)` context management.

#### Code Fix: Before vs. After
```diff
--- faulty_app.py
+++ corrected_app.py
-        try:
-            f = open(output_file, "w")
-            for item_id, total in self.sales_history.items():
-                f.write(f"Item ID: {item_id}, Total Sale: ${total}\n")
-            f.close()
-        except:
-            print("An error occurred.")
+        try:
+            with open(output_file, mode="w", encoding="utf-8") as f:
+                # write lines...
+                return True
+        except (IOError, OSError) as err:
+            print(f"[Error] Failed to write sales report: {err}")
+            return False
```

---

## 4. Code Optimization & Quality Improvements

In addition to fixing individual bugs, the following structural enhancements were made in `corrected_app.py`:
1. **Domain Model (`InventoryItem` dataclass)**: Centralized data validation, type conversion, and error checking upon loading.
2. **Context Managers (`with` statements)**: Enforced deterministic resource cleanup across all file I/O operations.
3. **ANSI Visual Polish**: Added colored status indicators in console output for better readability.
4. **Type Annotations**: Comprehensive PEP 484 type hints across all methods for maintainability and IDE static analysis.

---

## 5. Verification & Automated Test Results

The resolution of each bug was verified by executing `test_debugging.py`:
```bash
python test_debugging.py
```
**Results**:
- `test_fix_bug_1_instance_independence`: **PASS**
- `test_fix_bug_2_missing_file_handled_gracefully`: **PASS**
- `test_fix_bug_3_display_inventory_no_index_error`: **PASS**
- `test_fix_bug_4_and_5_order_processing_and_discount`: **PASS**
- `test_fix_bug_6_remove_consecutive_out_of_stock_items`: **PASS**
- `test_fix_bug_7_calculate_average_empty_category_no_division_by_zero`: **PASS**
- `test_fix_bug_8_export_sales_report`: **PASS**

All 7 test cases passed with zero regressions.
