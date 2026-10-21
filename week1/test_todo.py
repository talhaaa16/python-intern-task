"""
test_todo.py
Automated Unit Tests for the To-Do List Application.
Uses Python's standard library `unittest` framework (zero dependencies).
"""

import unittest
import os
import tempfile
import json
from datetime import datetime

from models import Task, TaskPriority, TaskStatus
from storage import StorageHandler
from manager import TaskManager


class TestTaskModel(unittest.TestCase):
    """Unit tests for the Task domain model."""

    def test_task_creation_defaults(self):
        """Test default values on Task instantiation."""
        task = Task(id=1, title="Test Task")
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "")
        self.assertEqual(task.priority, TaskPriority.MEDIUM)
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertIsNone(task.due_date)
        self.assertTrue(len(task.created_at) > 0)

    def test_mark_completed(self):
        """Test transitioning status to COMPLETED."""
        task = Task(id=1, title="Pending Task")
        task.mark_completed()
        self.assertEqual(task.status, TaskStatus.COMPLETED)

    def test_serialization_and_deserialization(self):
        """Test to_dict and from_dict roundtrip."""
        original = Task(
            id=42,
            title="Complex Task",
            description="With description",
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            due_date="2026-12-31",
            created_at="2026-10-18 10:00:00"
        )
        data = original.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["id"], 42)
        self.assertEqual(data["priority"], "High")
        self.assertEqual(data["status"], "In Progress")

        reconstructed = Task.from_dict(data)
        self.assertEqual(reconstructed.id, original.id)
        self.assertEqual(reconstructed.title, original.title)
        self.assertEqual(reconstructed.priority, original.priority)
        self.assertEqual(reconstructed.status, original.status)
        self.assertEqual(reconstructed.due_date, original.due_date)


class TestStorageHandler(unittest.TestCase):
    """Unit tests for StorageHandler persistence and error handling."""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.storage = StorageHandler(filepath=self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
        backup = f"{self.temp_file.name}.corrupt.bak"
        if os.path.exists(backup):
            os.remove(backup)

    def test_load_non_existent_file(self):
        """Test loading from a file that does not exist returns empty list."""
        non_existent_storage = StorageHandler(filepath="non_existent_file_xyz.json")
        self.assertEqual(non_existent_storage.load_tasks(), [])

    def test_save_and_load_tasks(self):
        """Test saving tasks atomically and reading them back."""
        sample_data = [
            {"id": 1, "title": "Task 1", "priority": "Low", "status": "Pending"},
            {"id": 2, "title": "Task 2", "priority": "High", "status": "Completed"}
        ]
        save_success = self.storage.save_tasks(sample_data)
        self.assertTrue(save_success)

        loaded_data = self.storage.load_tasks()
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]["title"], "Task 1")
        self.assertEqual(loaded_data[1]["status"], "Completed")

    def test_corrupted_json_recovery(self):
        """Test that corrupted JSON is caught and backed up gracefully."""
        with open(self.temp_file.name, "w") as f:
            f.write("{ invalid json corrupted content [")

        result = self.storage.load_tasks()
        self.assertEqual(result, [])
        self.assertTrue(os.path.exists(f"{self.temp_file.name}.corrupt.bak"))


class TestTaskManager(unittest.TestCase):
    """Unit tests for TaskManager business logic operations."""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.storage = StorageHandler(filepath=self.temp_file.name)
        self.manager = TaskManager(storage=self.storage)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_add_task_success(self):
        """Test adding a task with valid inputs."""
        task = self.manager.add_task(
            title="Buy groceries",
            description="Milk, eggs, coffee",
            priority=TaskPriority.HIGH,
            due_date="2026-10-31"
        )
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Buy groceries")
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertEqual(len(self.manager.tasks), 1)

    def test_add_task_empty_title_raises_error(self):
        """Test that adding a task with empty title raises ValueError."""
        with self.assertRaises(ValueError):
            self.manager.add_task(title="   ")

    def test_remove_task(self):
        """Test removing an existing task and a non-existent task."""
        task = self.manager.add_task(title="To be deleted")
        self.assertTrue(self.manager.remove_task(task.id))
        self.assertFalse(self.manager.remove_task(999))
        self.assertEqual(len(self.manager.tasks), 0)

    def test_update_status(self):
        """Test updating task status."""
        task = self.manager.add_task(title="In progress test")
        self.assertTrue(self.manager.update_status(task.id, TaskStatus.IN_PROGRESS))
        self.assertEqual(self.manager.get_task(task.id).status, TaskStatus.IN_PROGRESS)
        self.assertTrue(self.manager.mark_completed(task.id))
        self.assertEqual(self.manager.get_task(task.id).status, TaskStatus.COMPLETED)

    def test_search_and_filter(self):
        """Test listing tasks with status, priority, and keyword filters."""
        self.manager.add_task(title="Write code", priority=TaskPriority.HIGH, status=TaskStatus.COMPLETED)
        self.manager.add_task(title="Review PR", priority=TaskPriority.LOW, status=TaskStatus.PENDING)
        self.manager.add_task(title="Write tests", priority=TaskPriority.MEDIUM, status=TaskStatus.IN_PROGRESS)

        # Status filter
        completed = self.manager.list_tasks(status_filter=TaskStatus.COMPLETED)
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].title, "Write code")

        # Priority filter
        low_p = self.manager.list_tasks(priority_filter=TaskPriority.LOW)
        self.assertEqual(len(low_p), 1)
        self.assertEqual(low_p[0].title, "Review PR")

        # Keyword filter
        write_tasks = self.manager.list_tasks(keyword="write")
        self.assertEqual(len(write_tasks), 2)


if __name__ == "__main__":
    unittest.main()
