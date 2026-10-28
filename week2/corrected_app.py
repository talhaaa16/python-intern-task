"""
corrected_app.py
REFACTORED & CORRECTED INVENTORY AND SALES MANAGEMENT SYSTEM
Free of bugs, optimized for readability, and equipped with robust error handling.
"""

import csv
import os
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional


@dataclass
class InventoryItem:
    """Represents a validated inventory item."""
    id: str
    name: str
    category: str
    price: float
    stock: int

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "InventoryItem":
        """Factory method to parse and validate CSV string records."""
        try:
            return cls(
                id=str(data["id"]).strip(),
                name=str(data["name"]).strip(),
                category=str(data.get("category", "General")).strip(),
                price=round(float(data["price"]), 2),
                stock=int(data["stock"])
            )
        except (ValueError, KeyError) as err:
            raise ValueError(f"Malformed item data: {err}")


class InventoryManager:
    """
    Robust Inventory and Sales Manager.
    Fixes legacy bugs: mutable default arguments, resource leaks,
    off-by-one errors, type coercion mismatches, and list mutation issues.
    """

    # ANSI terminal colors
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    # FIX BUG 1: Use None as default and instantiate a new list per instance
    def __init__(self, inventory: Optional[List[InventoryItem]] = None):
        self.inventory: List[InventoryItem] = list(inventory) if inventory is not None else []
        self.sales_history: Dict[str, float] = {}

    def load_from_csv(self, filename: str = "sample_inventory.csv") -> bool:
        """
        FIX BUG 2 & BUG 4:
        - Uses 'with' context manager to guarantee file closure.
        - Catches FileNotFoundError and parsing errors gracefully.
        - Properly casts prices to float and stock to int.
        """
        if not os.path.exists(filename):
            print(f"{self.RED}[Error] Inventory file '{filename}' not found.{self.RESET}")
            return False

        try:
            with open(filename, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                loaded_count = 0
                for row_num, row in enumerate(reader, start=2):
                    try:
                        item = InventoryItem.from_dict(row)
                        self.inventory.append(item)
                        loaded_count += 1
                    except ValueError as parse_err:
                        print(f"{self.YELLOW}[Warning] Skipping invalid row #{row_num}: {parse_err}{self.RESET}")
                print(f"{self.GREEN}[✓] Successfully loaded {loaded_count} items from '{filename}'.{self.RESET}")
                return True
        except (IOError, OSError) as err:
            print(f"{self.RED}[Error] Failed to read inventory file: {err}{self.RESET}")
            return False

    def display_inventory(self) -> None:
        """
        FIX BUG 3:
        Direct iteration over elements avoids off-by-one loop index errors.
        Renders a clean, formatted table.
        """
        if not self.inventory:
            print(f"\n{self.YELLOW}--> Inventory is currently empty.{self.RESET}")
            return

        print("\n" + "=" * 75)
        print(f" {self.BOLD}{'ID':<6} │ {'Name':<28} │ {'Category':<14} │ {'Price':<9} │ {'Stock'}{self.RESET}")
        print("─" * 75)

        for item in self.inventory:
            stock_color = self.GREEN if item.stock > 10 else (self.YELLOW if item.stock > 0 else self.RED)
            print(
                f" {item.id:<6} │ {item.name:<28} │ {item.category:<14} │ "
                f"${item.price:<8.2f} │ {stock_color}{item.stock:<5}{self.RESET}"
            )

        print("─" * 75)
        print(f" Total items: {len(self.inventory)}")
        print("=" * 75)

    def process_order(self, item_id: str, quantity: int, discount_pct: float = 0.0) -> bool:
        """
        FIX BUG 4 & BUG 5:
        - Validates numeric inputs.
        - Checks available stock accurately.
        - Calculates discounted price using correct mathematical formula.
        """
        if quantity <= 0:
            print(f"{self.RED}[Error] Order quantity must be greater than zero.{self.RESET}")
            return False

        if not (0 <= discount_pct <= 100):
            print(f"{self.RED}[Error] Discount percentage must be between 0 and 100.{self.RESET}")
            return False

        target = next((item for item in self.inventory if item.id == str(item_id)), None)
        if not target:
            print(f"{self.RED}[Error] Item with ID '{item_id}' not found in inventory.{self.RESET}")
            return False

        if target.stock < quantity:
            print(f"{self.RED}[Error] Insufficient stock! Available: {target.stock}, Requested: {quantity}.{self.RESET}")
            return False

        # Correct formula: subtotal * (1 - discount / 100)
        subtotal = target.price * quantity
        discount_amount = subtotal * (discount_pct / 100.0)
        final_price = round(subtotal - discount_amount, 2)

        target.stock -= quantity
        self.sales_history[item_id] = self.sales_history.get(item_id, 0.0) + final_price

        print(
            f"{self.GREEN}[✓] Order processed: {quantity}x '{target.name}'. "
            f"Total = ${final_price:.2f} (Discount applied: {discount_pct}%). Remaining Stock: {target.stock}{self.RESET}"
        )
        return True

    def remove_out_of_stock_items(self) -> int:
        """
        FIX BUG 6:
        Uses a list comprehension to filter items without modifying the list
        in-place during iteration.
        """
        initial_count = len(self.inventory)
        self.inventory = [item for item in self.inventory if item.stock > 0]
        removed_count = initial_count - len(self.inventory)
        print(f"{self.GREEN}[✓] Cleaned inventory: Removed {removed_count} out-of-stock item(s).{self.RESET}")
        return removed_count

    def calculate_average_price(self, category: Optional[str] = None) -> float:
        """
        FIX BUG 7:
        Safeguards against ZeroDivisionError by checking count before dividing.
        """
        matching_items = [
            item for item in self.inventory
            if category is None or item.category.lower() == category.lower().strip()
        ]

        if not matching_items:
            print(f"{self.YELLOW}[Info] No items found matching category '{category}'. Average price is $0.00.{self.RESET}")
            return 0.0

        total_price = sum(item.price for item in matching_items)
        avg = round(total_price / len(matching_items), 2)
        return avg

    def export_sales_report(self, output_file: str = "sales_report.txt") -> bool:
        """
        FIX BUG 8:
        Replaces bare 'except:' with explicit exception catching and ensures
        file descriptor is safely managed via context manager.
        """
        try:
            with open(output_file, mode="w", encoding="utf-8") as f:
                f.write("=" * 50 + "\n")
                f.write("           INVENTORY SALES REPORT\n")
                f.write("=" * 50 + "\n")
                if not self.sales_history:
                    f.write("No sales recorded yet.\n")
                else:
                    grand_total = 0.0
                    for item_id, total in self.sales_history.items():
                        f.write(f"Item ID: {item_id:<8} | Total Revenue: ${total:>8.2f}\n")
                        grand_total += total
                    f.write("-" * 50 + "\n")
                    f.write(f"Grand Total Revenue: ${grand_total:.2f}\n")
            print(f"{self.GREEN}[✓] Sales report successfully exported to '{output_file}'.{self.RESET}")
            return True
        except (IOError, OSError) as err:
            print(f"{self.RED}[Error] Failed to write sales report: {err}{self.RESET}")
            return False


def interactive_menu():
    """Interactive CLI menu for manual testing and demonstration."""
    manager = InventoryManager()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "sample_inventory.csv")
    manager.load_from_csv(csv_path)

    while True:
        print("\n" + "=" * 50)
        print("   INVENTORY MANAGEMENT & DEBUGGED SYSTEM")
        print("=" * 50)
        print(" [1] Display Inventory")
        print(" [2] Process Customer Order")
        print(" [3] Remove Out of Stock Items")
        print(" [4] Calculate Average Price")
        print(" [5] Export Sales Report")
        print(" [6] Exit Application")

        try:
            choice = input("\nEnter choice (1-6): ").strip()
            if choice == "1":
                manager.display_inventory()
            elif choice == "2":
                item_id = input("Enter Item ID (e.g. 101): ").strip()
                qty_str = input("Enter Quantity: ").strip()
                disc_str = input("Enter Discount % (0-100, default 0): ").strip()
                qty = int(qty_str) if qty_str.isdigit() else -1
                disc = float(disc_str) if disc_str else 0.0
                manager.process_order(item_id, qty, disc)
            elif choice == "3":
                manager.remove_out_of_stock_items()
            elif choice == "4":
                cat = input("Enter Category (or press Enter for all): ").strip()
                avg = manager.calculate_average_price(category=cat if cat else None)
                print(f"Average Price: ${avg:.2f}")
            elif choice == "5":
                manager.export_sales_report()
            elif choice == "6":
                print("\nExiting. Thank you!")
                break
            else:
                print("[!] Invalid option. Enter 1-6.")
        except KeyboardInterrupt:
            print("\nExiting cleanly...")
            sys.exit(0)
        except Exception as e:
            print(f"[Error] Unexpected input error: {e}")


if __name__ == "__main__":
    interactive_menu()
