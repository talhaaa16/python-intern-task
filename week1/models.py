"""
models.py
Domain models and enumerations for the To-Do List Application.
"""

from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any


class TaskStatus(str, Enum):
    """Represents the possible completion states of a task."""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class TaskPriority(str, Enum):
    """Represents the urgency / priority levels of a task."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass
class Task:
    """
    Represents an individual Task entity.
    
    Attributes:
        id (int): Unique identifier for the task.
        title (str): Brief title or summary of the task.
        description (str): Detailed notes or description.
        priority (TaskPriority): Urgency level of the task.
        status (TaskStatus): Current state of completion.
        due_date (Optional[str]): Due date string formatted as YYYY-MM-DD.
        created_at (str): ISO-formatted timestamp when task was created.
    """
    id: int
    title: str
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    due_date: Optional[str] = None
    created_at: str = ""

    def __post_init__(self):
        """Set default created_at timestamp if not supplied."""
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(self.priority, str):
            try:
                self.priority = TaskPriority(self.priority)
            except ValueError:
                self.priority = TaskPriority.MEDIUM
        if isinstance(self.status, str):
            try:
                self.status = TaskStatus(self.status)
            except ValueError:
                self.status = TaskStatus.PENDING

    def mark_completed(self) -> None:
        """Transitions task status to COMPLETED."""
        self.status = TaskStatus.COMPLETED

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the Task object into a JSON-compatible dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "due_date": self.due_date,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """
        Factory method to reconstruct a Task object from dictionary data.
        
        Args:
            data (Dict[str, Any]): Dictionary containing task fields.
            
        Returns:
            Task: Reconstructed Task instance.
        """
        return cls(
            id=int(data["id"]),
            title=data.get("title", "Untitled Task"),
            description=data.get("description", ""),
            priority=TaskPriority(data.get("priority", TaskPriority.MEDIUM.value)),
            status=TaskStatus(data.get("status", TaskStatus.PENDING.value)),
            due_date=data.get("due_date"),
            created_at=data.get("created_at", ""),
        )
