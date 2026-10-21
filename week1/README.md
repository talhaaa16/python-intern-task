# Week 1: Python CLI Application - To-Do List Manager

A lightweight, robust, and modular Command-Line Interface (CLI) application for task management built with pure Python (Standard Library only).

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Design Decisions](#architecture--design-decisions)
3. [Folder & Module Structure](#folder--module-structure)
4. [Features](#features)
5. [Installation & Requirements](#installation--requirements)
6. [How to Run](#how-to-run)
7. [Manual Testing Scenarios](#manual-testing-scenarios)
8. [Deliverable Checklist](#deliverable-checklist)

---

## 1. Project Overview
This application fulfills the **Week 1 Task: Python CLI Application Design and Implementation**. It provides a complete To-Do List Manager where users can create, view, filter, complete, and remove tasks with automated persistent local storage.

---

## 2. Architecture & Design Decisions

### Architectural Pattern: Layered Modular Architecture
The application separates responsibilities into four distinct tiers:
- **Presentation Layer (`cli.py`, `main.py`)**: Interacts with the user, validates keyboard inputs, renders formatted tables, and isolates UI concerns.
- **Business Logic Layer (`manager.py`)**: Centralizes domain logic, maintains an in-memory index for $O(1)$ ID lookups, and triggers storage updates.
- **Domain Layer (`models.py`)**: Contains typed entities (`Task`, `TaskStatus`, `TaskPriority`) with clean serialization/deserialization logic.
- **Persistence Layer (`storage.py`)**: Handles read/write operations to `tasks.json`. Employs atomic write operations (`.tmp` file swapping) and catches corrupted JSON files safely with automatic backups.

### Flow Diagram & Logic

```
[User Input] 
     │
     ▼
[cli.py: CLIInterface]
  - Validates user input (non-empty title, numeric ID, YYYY-MM-DD date)
     │
     ▼
[manager.py: TaskManager]
  - Executes operation: add, delete, mark completed, list, search
     │
     ├───────────────► [models.py: Task] (Instantiates / updates Task object)
     │
     ▼
[storage.py: StorageHandler]
  - Writes to tasks.json.tmp -> Renames to tasks.json (Atomic Persistence)
```

---

## 3. Folder & Module Structure

```
week1/
├── architecture_plan.md   # Architectural blueprint and design specifications
├── cli.py                 # Presentation layer: formatted terminal UI and menus
├── main.py                # Application entry point with dependency injection
├── manager.py             # Business logic controller (TaskManager)
├── models.py              # Domain entities (Task, TaskStatus, TaskPriority)
├── package_deliverable.py # Self-contained ZIP packaging automation script
├── storage.py             # JSON persistence handler with error handling
├── task.md                # Week 1 internship task prompt
├── tasks.json             # Persistent JSON task database
├── test_todo.py           # Automated unit test suite (unittest framework)
├── week1_deliverable.zip  # Ready-to-submit archive bundle
└── README.md              # Comprehensive documentation and user manual
```

---

## 4. Features & Algorithms (Pseudo-code)

### Core Logic Pseudo-code (Task 8 & 9)
```
PROCEDURE AddTask(title, description, priority, due_date):
    IF title is EMPTY or whitespace THEN
        RAISE ValidationError("Title cannot be empty")
    END IF
    new_id = (MAX of existing IDs in memory) + 1 (or 1 if empty)
    task = NEW Task(id=new_id, title=title, priority=priority, status="Pending", ...)
    tasks_map[new_id] = task
    SAVE_TO_STORAGE(tasks_map)
    RETURN task
END PROCEDURE

PROCEDURE SaveToStorage(tasks_map):
    serialized_list = [task.to_dict() FOR task IN tasks_map.values()]
    WRITE serialized_list TO "tasks.json.tmp"
    ATOMIC_RENAME "tasks.json.tmp" -> "tasks.json"
END PROCEDURE

PROCEDURE UpdateStatus(task_id, new_status):
    IF task_id EXISTS in tasks_map THEN
        tasks_map[task_id].status = new_status
        SAVE_TO_STORAGE(tasks_map)
        RETURN TRUE
    END IF
    RETURN FALSE
END PROCEDURE
```

---

## 5. Installation & Requirements
- **Python Version**: Python 3.8 or higher.
- **Dependencies**: None (100% Python Standard Library: `json`, `datetime`, `enum`, `dataclasses`, `unittest`, `zipfile`).

---

## 6. How to Run

### Run the Interactive CLI Application:
```cmd
cmd /c cd week1 && python main.py
```
*(On Windows, you can also run `python main.py` or `py main.py` directly from within `week1`)*

### Run Automated Unit Tests (Task 15):
```cmd
cmd /c cd week1 && python test_todo.py
```
*(Runs comprehensive unit tests covering models, persistence, and task management)*

### Repackage Submission ZIP Archive (Deliverable 4 & 19):
```cmd
cmd /c cd week1 && python package_deliverable.py
```

---

## 7. Testing Scenarios

### A. Automated Unit Tests
The test suite in [`test_todo.py`](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/test_todo.py) tests:
- Model instantiation, default properties, and JSON serialization/deserialization.
- Persistence fault tolerance, atomic writes, and automatic corruption recovery.
- Task management operations: adding, deleting, updating status, and multi-field filtering.

### B. Manual Interactive Test Cases

| Test Case | Steps | Expected Result |
|---|---|---|
| **TC-01: Add Valid Task** | Select `[2]`, enter Title: `Submit Report`, Priority: `3`, Date: `2026-10-31` | Task created and displayed with High priority and due date. |
| **TC-02: Empty Title Validation** | Select `[2]`, hit Enter without typing a title | Application prompts `[!] Title cannot be empty` and re-prompts without crashing. |
| **TC-03: Invalid Date Format** | Select `[2]`, enter title `Fix bug`, enter due date `31-12-2026` | Application warns `[!] Invalid date format` and prompts again. |
| **TC-04: Update Status** | Select `[3]`, enter ID `1`, select `[2] In Progress` | Task #1 status changes to `⚡ In Progress` (cyan). |
| **TC-05: Filter by Priority** | Select `[5] -> [2]`, choose `High` | Only High priority tasks are displayed. |
| **TC-06: Remove Task with Confirmation** | Select `[4]`, enter ID `1`, type `y` | Task #1 is permanently deleted from list and `tasks.json`. |
| **TC-07: Persistence Check** | Exit via `[6]`, restart with `python main.py`, select `[1]` | All previously saved tasks remain intact. |

---

## 8. Evaluation Criteria Mapping (Tasks 1 - 19)

| Task Requirement | Implementation Location | Description |
|:---|:---|:---|
| **Items 1–3**: CLI To-Do application & clean OOP design | [`models.py`](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/models.py), [`manager.py`](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/manager.py) | Fully modular OOP architecture separating concerns. |
| **Items 4–5**: Self-contained ZIP archive, README, inline docstrings | [`week1_deliverable.zip`](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/week1_deliverable.zip), [`README.md`](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/README.md) | Packaged deliverable with docstrings on every function and class. |
| **Items 6–8**: Architecture plan, modules, flowcharts & pseudo-code | [`architecture_plan.md`](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/architecture_plan.md) | Full architectural blueprint, mermaid diagrams, and pseudo-code. |
| **Items 9–10**: Core features (Add, Remove, View, Update status) | [`manager.py`](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/manager.py), [`cli.py`](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/cli.py) | Full CRUD + status updates + keyword searching. |
| **Items 11–12**: Robust error handling & user input validation | [`cli.py`](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/cli.py), [`storage.py`](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/storage.py) | Empty title validation, date format checks, safe corrupted-file recovery. |
| **Items 13–14**: Clear documentation & design decisions | [`README.md`](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/README.md) | Exhaustive user manual, architecture guide, and setup instructions. |
| **Item 15**: Manual & automated testing instructions | [`test_todo.py`](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/test_todo.py), Section 7 above | 10 unit test cases + 7 manual test procedures. |
| **Items 16–19**: Evaluation criteria readiness & self-contained package | [`week1_deliverable.zip`](file:///c:/Users/Talha/OneDrive/Desktop/YuvaIntern-Python/week1/week1_deliverable.zip) | Standalone package runs on standard Python environments without external dependencies. |
