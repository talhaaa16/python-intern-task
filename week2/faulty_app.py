"""
faulty_app.py
LEGACY / BUGGY INVENTORY AND SALES MANAGEMENT SCRIPT
Contains multiple real-world bugs for Week 2 Debugging & Troubleshooting.
"""

import csv
import os


class InventoryManager:
    # BUG 1: Mutable default argument! Shared list between all instances
    def __init__(self, inventory=[]):
        self.inventory = inventory
        self.sales_history = {}

    def load_from_csv(self, filename="sample_inventory.csv"):
        # BUG 2: No context manager ('with' statement) and no FileNotFoundError handling
        file = open(filename, "r")
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            # BUG 4: Storing price and stock as raw strings instead of float/int!
            item = {
                "id": row[0],
                "name": row[1],
                "category": row[2],
                "price": row[3],      # String!
                "stock": row[4]       # String!
            }
            self.inventory.append(item)
        # Note: file is never closed! Resource leak.

    def display_inventory(self):
        print("\n--- Current Inventory ---")
        # BUG 3: Off-by-one loop error! Causes IndexError on the last iteration
        for i in range(len(self.inventory) + 1):
            item = self.inventory[i]
            print(f"[{item['id']}] {item['name']} - ${item['price']} (Stock: {item['stock']})")

    def process_order(self, item_id, quantity, discount_pct=0):
        # Find item
        target = None
        for item in self.inventory:
            if item["id"] == item_id:
                target = item
                break

        if not target:
            print("Item not found!")
            return False

        # BUG 4 (cont.): Comparing string stock to integer quantity
        if target["stock"] < quantity:
            print("Not enough stock!")
            return False

        # BUG 5: Logical bug in price calculation due to string multiplication / order of operations
        raw_price = target["price"] * quantity
        final_price = raw_price - raw_price * discount_pct / 100

        target["stock"] = target["stock"] - quantity
        self.sales_history[item_id] = final_price
        print(f"Order processed: Total = ${final_price}")
        return True

    def remove_out_of_stock_items(self):
        # BUG 6: Mutating a list while iterating over it with for item in self.inventory!
        # This causes items to be skipped due to index shifts
        for item in self.inventory:
            if int(item["stock"]) <= 0:
                self.inventory.remove(item)
        print("Out of stock items removed.")

    def calculate_average_price(self, category=None):
        # BUG 7: ZeroDivisionError if inventory is empty or category has 0 items
        total = 0
        count = 0
        for item in self.inventory:
            if category is None or item["category"] == category:
                total += float(item["price"])
                count += 1
        # No check for count == 0!
        return total / count

    def export_sales_report(self, output_file="sales_report.txt"):
        # BUG 8: Bare except: hides critical errors, and mode 'w' overwrites without confirmation
        try:
            f = open(output_file, "w")
            for item_id, total in self.sales_history.items():
                f.write(f"Item ID: {item_id}, Total Sale: ${total}\n")
            f.close()
            print("Report exported successfully.")
        except:
            print("An error occurred.")


def main():
    manager = InventoryManager()
    manager.load_from_csv("sample_inventory.csv")
    manager.display_inventory()


if __name__ == "__main__":
    main()
