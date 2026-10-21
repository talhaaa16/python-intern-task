"""
cli.py
Command-Line Interface (CLI) view and controller for interactive user experience.
"""

import sys
from datetime import datetime
from typing import Optional
from models import TaskPriority, TaskStatus
from manager import TaskManager


class CLIInterface:
    """
    Console Presentation Layer.
    Provides styled menus, input prompts, formatted tabular outputs, and validation.
    """

    # ANSI Colors for enhanced terminal UX (gracefully supported in modern terminals)
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    def __init__(self, manager: TaskManager):
        """
        Initializes CLI Interface with the business logic manager.
        
        Args:
            manager (TaskManager): Task management controller.
        """
        self.manager = manager

    def print_banner(self) -> None:
        """Prints the application greeting banner."""
        print(f"\n{self.CYAN}{self.BOLD}" + "=" * 62)
        print("          TODO LIST MANAGER - PYTHON CLI APPLICATION")
        print("=" * 62 + f"{self.RESET}")

    def print_menu(self) -> None:
        """Displays available user actions."""
        print(f"\n{self.BOLD}Main Menu Options:{self.RESET}")
        print(" [1] View All Tasks")
        print(" [2] Add New Task")
        print(" [3] Update Task Status (In Progress / Completed)")
        print(" [4] Remove / Delete Task")
        print(" [5] Search & Filter Tasks")
        print(" [6] Exit Application")

    def run(self) -> None:
        """Main execution loop for user commands."""
        self.print_banner()

        while True:
            try:
                self.print_menu()
                choice = input(f"\n{self.BOLD}Enter choice (1-6): {self.RESET}").strip()

                if choice == "1":
                    self.handle_view_tasks()
                elif choice == "2":
                    self.handle_add_task()
                elif choice == "3":
                    self.handle_mark_completed()
                elif choice == "4":
                    self.handle_remove_task()
                elif choice == "5":
                    self.handle_search_filter()
                elif choice == "6":
                    print(f"\n{self.GREEN}Thank you for using To-Do List Manager. Goodbye!{self.RESET}\n")
                    break
                else:
                    print(f"{self.RED}[!] Invalid choice. Please enter a number between 1 and 6.{self.RESET}")
            except KeyboardInterrupt:
                print(f"\n\n{self.YELLOW}Session interrupted. Exiting cleanly...{self.RESET}\n")
                sys.exit(0)
            except Exception as e:
                print(f"{self.RED}[!] Unexpected error occurred: {e}{self.RESET}")

    def handle_view_tasks(self, tasks=None) -> None:
        """Renders tasks in an aesthetically pleasing tabular view with status badges."""
        if tasks is None:
            tasks = self.manager.list_tasks()

        if not tasks:
            print(f"\n{self.YELLOW}--> No tasks found in your to-do list.{self.RESET}")
            return

        print("\n" + "=" * 80)
        print(f" {self.BOLD}{'ID':<4} │ {'Status':<15} │ {'Priority':<10} │ {'Due Date':<12} │ {'Title'}{self.RESET}")
        print("─" * 80)

        completed_cnt = 0
        in_progress_cnt = 0
        pending_cnt = 0

        for task in tasks:
            # Status badge styling
            if task.status == TaskStatus.COMPLETED:
                status_str = f"{self.GREEN}✔ Completed   {self.RESET}"
                completed_cnt += 1
            elif task.status == TaskStatus.IN_PROGRESS:
                status_str = f"{self.CYAN}⚡ In Progress {self.RESET}"
                in_progress_cnt += 1
            else:
                status_str = f"{self.YELLOW}⏳ Pending     {self.RESET}"
                pending_cnt += 1

            # Priority badge styling
            if task.priority == TaskPriority.HIGH:
                p_str = f"{self.RED}{self.BOLD}▲ High    {self.RESET}"
            elif task.priority == TaskPriority.MEDIUM:
                p_str = f"{self.YELLOW}■ Medium  {self.RESET}"
            else:
                p_str = f"{self.DIM}▼ Low     {self.RESET}"

            due = task.due_date if task.due_date else "No due date"

            print(f" {task.id:<4} │ {status_str} │ {p_str} │ {due:<12} │ {self.BOLD}{task.title}{self.RESET}")
            if task.description:
                print(f"      │ {self.DIM}↳ Notes: {task.description}{self.RESET}")

        print("─" * 80)
        print(
            f" {self.BOLD}Summary:{self.RESET} Total: {len(tasks)}  "
            f"│  {self.GREEN}Completed: {completed_cnt}{self.RESET}  "
            f"│  {self.CYAN}In Progress: {in_progress_cnt}{self.RESET}  "
            f"│  {self.YELLOW}Pending: {pending_cnt}{self.RESET}"
        )
        print("=" * 80)

    def handle_add_task(self) -> None:
        """Interactively gathers input to create a new task."""
        print(f"\n{self.CYAN}--- Add New Task ---{self.RESET}")
        
        while True:
            title = input("Enter task title (required): ").strip()
            if title:
                break
            print(f"{self.RED}[!] Title cannot be empty. Please enter a valid title.{self.RESET}")

        description = input("Enter description (optional, press Enter to skip): ").strip()

        # Priority selection
        print("Select Priority:")
        print("  [1] Low")
        print("  [2] Medium (Default)")
        print("  [3] High")
        priority_choice = input("Choice (1-3, default 2): ").strip()
        priority_map = {
            "1": TaskPriority.LOW,
            "2": TaskPriority.MEDIUM,
            "3": TaskPriority.HIGH
        }
        priority = priority_map.get(priority_choice, TaskPriority.MEDIUM)

        # Due date selection with format verification
        due_date: Optional[str] = None
        while True:
            due_input = input("Enter due date (YYYY-MM-DD or press Enter to skip): ").strip()
            if not due_input:
                break
            try:
                datetime.strptime(due_input, "%Y-%m-%d")
                due_date = due_input
                break
            except ValueError:
                print(f"{self.RED}[!] Invalid date format. Please use YYYY-MM-DD (e.g. 2026-12-31).{self.RESET}")

        task = self.manager.add_task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        print(f"\n{self.GREEN}[✓] Task #{task.id} '{task.title}' added successfully!{self.RESET}")

    def handle_mark_completed(self) -> None:
        """Prompts for an ID and updates task status."""
        print(f"\n{self.CYAN}--- Update Task Status ---{self.RESET}")
        id_str = input("Enter Task ID: ").strip()

        if not id_str.isdigit():
            print(f"{self.RED}[!] Invalid ID. Please enter numeric digits only.{self.RESET}")
            return

        task_id = int(id_str)
        task = self.manager.get_task(task_id)
        if not task:
            print(f"{self.RED}[!] Task #{task_id} was not found.{self.RESET}")
            return

        print(f"Current Status of Task #{task_id} ('{task.title}'): {task.status.value}")
        print("Select New Status:")
        print("  [1] Completed (Default)")
        print("  [2] In Progress")
        print("  [3] Pending")
        choice = input("Choice (1-3, default 1): ").strip()

        status_map = {
            "1": TaskStatus.COMPLETED,
            "2": TaskStatus.IN_PROGRESS,
            "3": TaskStatus.PENDING,
            "": TaskStatus.COMPLETED
        }
        new_status = status_map.get(choice, TaskStatus.COMPLETED)
        self.manager.update_status(task_id, new_status)
        print(f"{self.GREEN}[✓] Task #{task_id} status updated to '{new_status.value}'.{self.RESET}")

    def handle_remove_task(self) -> None:
        """Prompts for an ID and deletes that task."""
        print(f"\n{self.CYAN}--- Remove / Delete Task ---{self.RESET}")
        id_str = input("Enter Task ID to remove: ").strip()

        if not id_str.isdigit():
            print(f"{self.RED}[!] Invalid ID. Please enter numeric digits only.{self.RESET}")
            return

        task_id = int(id_str)
        task = self.manager.get_task(task_id)
        if not task:
            print(f"{self.RED}[!] Task #{task_id} does not exist.{self.RESET}")
            return

        confirm = input(f"Are you sure you want to delete '{task.title}'? (y/N): ").strip().lower()
        if confirm == "y":
            self.manager.remove_task(task_id)
            print(f"{self.GREEN}[✓] Task #{task_id} removed successfully.{self.RESET}")
        else:
            print(f"{self.YELLOW}Deletion cancelled.{self.RESET}")

    def handle_search_filter(self) -> None:
        """Filter tasks by status, priority, or search keyword."""
        print(f"\n{self.CYAN}--- Search & Filter Options ---{self.RESET}")
        print(" [1] Filter by Status (Pending / Completed)")
        print(" [2] Filter by Priority (Low / Medium / High)")
        print(" [3] Search by Keyword in Title/Description")
        sub_choice = input("Enter filter option (1-3): ").strip()

        if sub_choice == "1":
            print("Select Status: [1] Pending  [2] Completed")
            s = input("Choice (1 or 2): ").strip()
            status = TaskStatus.PENDING if s == "1" else TaskStatus.COMPLETED if s == "2" else None
            if status:
                filtered = self.manager.list_tasks(status_filter=status)
                self.handle_view_tasks(filtered)
            else:
                print(f"{self.RED}[!] Invalid status choice.{self.RESET}")

        elif sub_choice == "2":
            print("Select Priority: [1] Low  [2] Medium  [3] High")
            p = input("Choice (1-3): ").strip()
            p_map = {"1": TaskPriority.LOW, "2": TaskPriority.MEDIUM, "3": TaskPriority.HIGH}
            priority = p_map.get(p)
            if priority:
                filtered = self.manager.list_tasks(priority_filter=priority)
                self.handle_view_tasks(filtered)
            else:
                print(f"{self.RED}[!] Invalid priority choice.{self.RESET}")

        elif sub_choice == "3":
            kw = input("Enter search keyword: ").strip()
            if kw:
                filtered = self.manager.list_tasks(keyword=kw)
                self.handle_view_tasks(filtered)
            else:
                print(f"{self.YELLOW}Empty search term entered.{self.RESET}")
        else:
            print(f"{self.RED}[!] Invalid filter selection.{self.RESET}")
