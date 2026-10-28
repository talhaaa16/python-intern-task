"""
package_deliverable.py
Packaging script to generate the self-contained ZIP archive for Week 2 submission.
"""

import os
import zipfile

FILES_TO_INCLUDE = [
    "faulty_app.py",
    "corrected_app.py",
    "reproduce_bugs.py",
    "test_debugging.py",
    "sample_inventory.csv",
    "debugging_log.md",
    "README.md",
    "WEEK2_FULL_SUBMISSION.md",
    "task.md"
]

OUTPUT_ZIP = "week2_deliverable.zip"


def create_archive():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(base_dir, OUTPUT_ZIP)

    print(f"Creating Week 2 submission package: {OUTPUT_ZIP}...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename in FILES_TO_INCLUDE:
            filepath = os.path.join(base_dir, filename)
            if os.path.exists(filepath):
                zip_file.write(filepath, arcname=filename)
                print(f"  [+] Included: {filename}")
            else:
                print(f"  [!] Skipped (not found): {filename}")

    size_kb = os.path.getsize(zip_path) / 1024
    print(f"\n[✓] Week 2 archive successfully created: {zip_path} ({size_kb:.2f} KB)")


if __name__ == "__main__":
    create_archive()
