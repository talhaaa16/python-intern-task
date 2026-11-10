"""
package_deliverable.py
Packaging script to generate the self-contained ZIP archive for Week 4 submission.
"""

import os
import zipfile

FILES_TO_INCLUDE = [
    "baseline_app.py",
    "optimized_app.py",
    "profiler_benchmarks.py",
    "test_equivalence.py",
    "profiling_report.md",
    "WEEK4_FULL_SUBMISSION.md",
    "README.md",
    "task.md"
]

OUTPUT_ZIP = "week4_deliverable.zip"


def create_archive():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(base_dir, OUTPUT_ZIP)

    print(f"Creating Week 4 submission package: {OUTPUT_ZIP}...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename in FILES_TO_INCLUDE:
            filepath = os.path.join(base_dir, filename)
            if os.path.exists(filepath):
                zip_file.write(filepath, arcname=filename)
                print(f"  [+] Included: {filename}")
            else:
                print(f"  [!] Skipped (not found): {filename}")

    size_kb = os.path.getsize(zip_path) / 1024
    print(f"\n[✓] Week 4 archive successfully created: {zip_path} ({size_kb:.2f} KB)")


if __name__ == "__main__":
    create_archive()

