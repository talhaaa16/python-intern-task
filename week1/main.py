"""
main.py
Application Entry Point for To-Do List Manager CLI.
"""

import sys
import os
from storage import StorageHandler
from manager import TaskManager
from cli import CLIInterface


def main():
    """
    Initializes dependencies and launches the CLI application loop.
    """
    # Determine the directory of main.py to store tasks.json alongside the script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    storage_path = os.path.join(base_dir, "tasks.json")

    # Dependency Injection: Storage -> Manager -> View
    storage = StorageHandler(filepath=storage_path)
    manager = TaskManager(storage=storage)
    app = CLIInterface(manager=manager)

    # Launch interface
    app.run()


if __name__ == "__main__":
    main()
