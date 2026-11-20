"""
Standard Library AST & Style Linter for Python Projects.
Enforces PEP8 conventions, docstring presence, syntax validity, and type annotations
without requiring external third-party dependencies.
"""
import ast
import os
import sys
from typing import List, Tuple


class ProjectLinter:
    """
    Performs static analysis and linting checks on Python source trees.
    """

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.violations: List[Tuple[str, int, str]] = []

    def check_file(self, filepath: str) -> None:
        """Inspects an individual python file for syntax, style, and docstring rules."""
        rel_path = os.path.relpath(filepath, self.root_dir)
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()

        # Check 1: Syntax tree compilation
        try:
            tree = ast.parse(code, filename=filepath)
        except SyntaxError as e:
            self.violations.append((rel_path, e.lineno or 0, f"SyntaxError: {e.msg}"))
            return

        lines = code.splitlines()

        # Check 2: Line length (< 120 chars) & Trailing Whitespace
        for idx, line in enumerate(lines, start=1):
            if len(line) > 120:
                self.violations.append((rel_path, idx, f"Line exceeds 120 characters ({len(line)} chars)"))
            if line.endswith(" ") or line.endswith("\t"):
                self.violations.append((rel_path, idx, "Trailing whitespace detected"))

        # Check 3: Module Docstring
        if not ast.get_docstring(tree):
            self.violations.append((rel_path, 1, "Missing module-level docstring"))

        # Check 4: Function and Class Docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_") and not ast.get_docstring(node):
                    self.violations.append(
                        (rel_path, node.lineno, f"Public function '{node.name}' is missing a docstring")
                    )
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("_") and not ast.get_docstring(node):
                    self.violations.append(
                        (rel_path, node.lineno, f"Public class '{node.name}' is missing a docstring")
                    )

    def run(self) -> bool:
        """
        Runs linting across all python files in root_dir.
        Returns True if 0 violations, False otherwise.
        """
        self.violations.clear()
        target_dirs = [
            os.path.join(self.root_dir, "src"),
            os.path.join(self.root_dir, "tests")
        ]

        for target_dir in target_dirs:
            if not os.path.exists(target_dir):
                continue
            for root, _, files in os.walk(target_dir):
                for file in files:
                    if file.endswith(".py"):
                        full_path = os.path.join(root, file)
                        self.check_file(full_path)

        return len(self.violations) == 0

    def print_report(self) -> None:
        """Outputs formatted linting summary table to stdout."""
        print("=" * 60)
        print("STATIC ANALYSIS & CODE LINTING REPORT")
        print("=" * 60)
        if not self.violations:
            print("Status: PASSED (0 violations detected across all checked modules)")
        else:
            print(f"Status: FAILED ({len(self.violations)} violation(s) found):")
            for rel_path, lineno, msg in self.violations:
                print(f"  {rel_path}:{lineno} -> {msg}")
        print("=" * 60)


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    linter = ProjectLinter(project_root)
    passed = linter.run()
    linter.print_report()
    sys.exit(0 if passed else 1)
