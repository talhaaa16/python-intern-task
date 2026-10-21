"""
package_deliverable.py
Utility script to package all Week 1 Python code files, documentation,
and test suite into a clean, self-contained ZIP archive for submission.
"""

import os
import zipfile

FILES_TO_INCLUDE = [
    "main.py",
    "cli.py",
    "manager.py",
    "models.py",
    "storage.py",
    "test_todo.py",
    "tasks.json",
    "architecture_plan.md",
    "README.md",
    "task.md"
]

OUTPUT_ZIP = "week1_deliverable.zip"


def create_archive():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(base_dir, OUTPUT_ZIP)

    print(f"Creating submission package: {OUTPUT_ZIP}...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename in FILES_TO_INCLUDE:
            filepath = os.path.join(base_dir, filename)
            if os.path.exists(filepath):
                zip_file.write(filepath, arcname=filename)
                print(f"  [+] Included: {filename}")
            else:
                print(f"  [!] Skipped (not found): {filename}")

    size_kb = os.path.getsize(zip_path) / 1024
    print(f"\n[✓] Deliverable archive successfully created: {zip_path} ({size_kb:.2f} KB)")


if __name__ == "__main__":
    create_archive()
