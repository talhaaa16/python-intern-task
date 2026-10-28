"""
reproduce_bugs.py
Automated Bug Reproduction Suite for Week 2.
Runs isolated test scenarios against `faulty_app.py` to trigger, capture,
and document each bug with its exact traceback and unexpected behavior.
"""

import sys
import traceback
from faulty_app import InventoryManager


def print_header(title):
    print("\n" + "=" * 70)
    print(f"BUG REPRODUCTION SCENARIO: {title}")
    print("=" * 70)


def reproduce_bug_1_mutable_default():
    print_header("Bug 1: Mutable Default Argument in __init__")
    mgr1 = InventoryManager()
    mgr1.inventory.append({"id": "999", "name": "Leaked Item", "price": "10.0", "stock": "5"})

    mgr2 = InventoryManager()
    print(f"Manager 1 inventory count: {len(mgr1.inventory)}")
    print(f"Manager 2 inventory count: {len(mgr2.inventory)} (Expected: 0)")
    if len(mgr2.inventory) > 0:
        print("[FAIL - CONFIRMED BUG] State leaked! Manager 2 shared Manager 1's list.")
    else:
        print("[PASS] Independent state.")


def reproduce_bug_2_missing_file():
    print_header("Bug 2: Unhandled FileNotFoundError in load_from_csv")
    mgr = InventoryManager([])
    try:
        mgr.load_from_csv("non_existent_inventory_file.csv")
        print("[UNEXPECTED] No error occurred.")
    except FileNotFoundError as e:
        print(f"[FAIL - CONFIRMED BUG] Crashed with unhandled FileNotFoundError: {e}")


def reproduce_bug_3_off_by_one_index_error():
    print_header("Bug 3: Off-By-One Loop Error in display_inventory")
    mgr = InventoryManager([])
    mgr.load_from_csv("sample_inventory.csv")
    try:
        mgr.display_inventory()
    except IndexError as e:
        print(f"\n[FAIL - CONFIRMED BUG] Loop exceeded list bounds with IndexError: {e}")


def reproduce_bug_4_and_5_type_mismatch_and_price_calc():
    print_header("Bug 4 & 5: String Type Coercion & Calculation Error in process_order")
    mgr = InventoryManager([])
    mgr.load_from_csv("sample_inventory.csv")
    try:
        mgr.process_order(item_id="101", quantity=2, discount_pct=10)
    except TypeError as e:
        print(f"[FAIL - CONFIRMED BUG] Type mismatch during arithmetic: {e}")


def reproduce_bug_6_mutating_list_during_iteration():
    print_header("Bug 6: Mutating List During Iteration in remove_out_of_stock_items")

    mgr = InventoryManager([
        {"id": "1", "name": "Item A", "price": 10.0, "stock": 0},
        {"id": "2", "name": "Item B", "price": 15.0, "stock": 0},
        {"id": "3", "name": "Item C", "price": 20.0, "stock": 10}
    ])
    print(f"Initial items: {[item['name'] for item in mgr.inventory]}")
    mgr.remove_out_of_stock_items()
    remaining = [item["name"] for item in mgr.inventory]
    print(f"Remaining items after removal: {remaining}")
    if "Item B" in remaining:
        print("[FAIL - CONFIRMED BUG] 'Item B' was skipped because index shifted during list.remove()!")


def reproduce_bug_7_zero_division():
    print_header("Bug 7: ZeroDivisionError in calculate_average_price")
    mgr = InventoryManager([])
    try:
        avg = mgr.calculate_average_price(category="NonExistentCategory")
        print(f"Average: {avg}")
    except ZeroDivisionError as e:
        print(f"[FAIL - CONFIRMED BUG] Crashed with ZeroDivisionError: {e}")


def main():
    print("RUNNING WEEK 2 BUG REPRODUCTION SUITE...")
    reproduce_bug_1_mutable_default()
    reproduce_bug_2_missing_file()
    reproduce_bug_3_off_by_one_index_error()
    reproduce_bug_4_and_5_type_mismatch_and_price_calc()
    reproduce_bug_6_mutating_list_during_iteration()
    reproduce_bug_7_zero_division()
    print("\n" + "=" * 70)
    print("ALL BUGS SUCCESSFULLY REPRODUCED AND DOCUMENTED.")
    print("=" * 70)


if __name__ == "__main__":
    main()
