"""
storage.py
Handles persistent storage operations (JSON file I/O) with error handling.
"""

import json
import os
import shutil
from typing import List, Dict, Any


class StorageHandler:
    """
    Manages persistence of tasks into a local JSON file.
    
    Provides fault tolerance: creates files on the fly, validates syntax,
    and safeguards existing data against corruption.
    """

    def __init__(self, filepath: str = "tasks.json"):
        """
        Initializes the storage handler with a target JSON file path.
        
        Args:
            filepath (str): Path to the persistence JSON file.
        """
        self.filepath = filepath

    def load_tasks(self) -> List[Dict[str, Any]]:
        """
        Reads tasks from the JSON file.
        
        Returns:
            List[Dict[str, Any]]: List of task dictionaries. If the file does not
            exist, returns an empty list. In case of file corruption, a backup
            is created and an empty list is returned to prevent crashes.
        """
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            # Create a backup of the corrupted file and initialize fresh state
            backup_path = f"{self.filepath}.corrupt.bak"
            shutil.copyfile(self.filepath, backup_path)
            print(f"[Warning] Corrupted data file detected! Backed up to {backup_path}.")
            return []
        except (IOError, OSError) as err:
            print(f"[Error] Failed to read storage file: {err}")
            return []

    def save_tasks(self, tasks_data: List[Dict[str, Any]]) -> bool:
        """
        Persists tasks data into the JSON file using an atomic write pattern.
        
        Args:
            tasks_data (List[Dict[str, Any]]): List of task data dictionaries.
            
        Returns:
            bool: True if saving succeeded, False otherwise.
        """
        temp_filepath = f"{self.filepath}.tmp"
        try:
            with open(temp_filepath, "w", encoding="utf-8") as temp_file:
                json.dump(tasks_data, temp_file, indent=4, ensure_ascii=False)
            
            # Atomic replace to prevent partial/corrupted writes
            if os.path.exists(self.filepath):
                os.replace(temp_filepath, self.filepath)
            else:
                os.rename(temp_filepath, self.filepath)
            return True
        except (IOError, OSError) as err:
            print(f"[Error] Failed to write storage file: {err}")
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
            return False
