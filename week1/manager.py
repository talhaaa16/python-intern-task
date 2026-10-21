"""
manager.py
Encapsulates all business logic for managing tasks in the application.
"""

from typing import List, Optional, Dict
from models import Task, TaskPriority, TaskStatus
from storage import StorageHandler


class TaskManager:
    """
    Controller responsible for business operations on tasks.
    Maintains an in-memory dictionary of tasks for fast lookup and interacts
    with StorageHandler for state persistence.
    """

    def __init__(self, storage: Optional[StorageHandler] = None):
        """
        Initializes the TaskManager and synchronizes with storage.
        
        Args:
            storage (Optional[StorageHandler]): Storage instance; defaults to new instance.
        """
        self.storage = storage or StorageHandler()
        self.tasks: Dict[int, Task] = {}
        self._load_from_storage()

    def _load_from_storage(self) -> None:
        """Loads tasks from persistent storage into in-memory structure."""
        raw_list = self.storage.load_tasks()
        self.tasks.clear()
        for item in raw_list:
            try:
                task = Task.from_dict(item)
                self.tasks[task.id] = task
            except (KeyError, ValueError) as e:
                print(f"[Warning] Skipping malformed record: {e}")

    def _save_to_storage(self) -> bool:
        """Serializes current in-memory tasks and writes to storage."""
        data = [task.to_dict() for task in self.tasks.values()]
        return self.storage.save_tasks(data)

    def _generate_next_id(self) -> int:
        """Calculates the next available integer task ID."""
        if not self.tasks:
            return 1
        return max(self.tasks.keys()) + 1

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[str] = None,
        status: TaskStatus = TaskStatus.PENDING
    ) -> Task:
        """
        Adds a new task to the task list and persists it.
        
        Args:
            title (str): Non-empty task title.
            description (str): Optional details.
            priority (TaskPriority): Priority level.
            due_date (Optional[str]): Due date in YYYY-MM-DD.
            status (TaskStatus): Initial task status. Defaults to PENDING.
            
        Returns:
            Task: The newly created Task object.
            
        Raises:
            ValueError: If the title is blank.
        """
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Task title cannot be empty.")

        task_id = self._generate_next_id()
        task = Task(
            id=task_id,
            title=clean_title,
            description=description.strip(),
            priority=priority,
            status=status,
            due_date=due_date.strip() if due_date else None
        )

        self.tasks[task_id] = task
        self._save_to_storage()
        return task

    def clear_all_tasks(self) -> bool:
        """Removes all tasks from memory and storage."""
        self.tasks.clear()
        return self._save_to_storage()

    def update_status(self, task_id: int, status: TaskStatus) -> bool:
        """
        Updates the status of an existing task.
        
        Args:
            task_id (int): Target task identifier.
            status (TaskStatus): New status to assign.
            
        Returns:
            bool: True if updated, False if task was not found.
        """
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            self._save_to_storage()
            return True
        return False

    def remove_task(self, task_id: int) -> bool:
        """
        Removes a task by its ID.
        
        Args:
            task_id (int): The ID of the task to delete.
            
        Returns:
            bool: True if task was deleted, False if ID was not found.
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_to_storage()
            return True
        return False

    def mark_completed(self, task_id: int) -> bool:
        """
        Marks an existing task as completed.
        
        Args:
            task_id (int): Target task identifier.
            
        Returns:
            bool: True if marked completed, False if not found.
        """
        if task_id in self.tasks:
            self.tasks[task_id].mark_completed()
            self._save_to_storage()
            return True
        return False

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieves a single task by ID.
        
        Args:
            task_id (int): Target task identifier.
            
        Returns:
            Optional[Task]: Task instance or None.
        """
        return self.tasks.get(task_id)

    def list_tasks(
        self,
        status_filter: Optional[TaskStatus] = None,
        priority_filter: Optional[TaskPriority] = None,
        keyword: Optional[str] = None
    ) -> List[Task]:
        """
        Retrieves a sorted list of tasks matching the specified criteria.
        
        Args:
            status_filter (Optional[TaskStatus]): Filter by task status.
            priority_filter (Optional[TaskPriority]): Filter by priority.
            keyword (Optional[str]): Substring search across title and description.
            
        Returns:
            List[Task]: Filtered list of Task instances sorted by ID.
        """
        results = list(self.tasks.values())

        if status_filter:
            results = [t for t in results if t.status == status_filter]

        if priority_filter:
            results = [t for t in results if t.priority == priority_filter]

        if keyword:
            term = keyword.lower().strip()
            results = [
                t for t in results 
                if term in t.title.lower() or term in t.description.lower()
            ]

        return sorted(results, key=lambda t: t.id)
