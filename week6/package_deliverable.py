"""
Packaging script to generate the self-contained ZIP archive for Week 6 submission.
Packages all source code, test suites, CI workflows, and documentation into week6_deliverable.zip.
"""
import os
import zipfile

def package_week6():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    zip_filename = os.path.join(script_dir, "week6_deliverable.zip")
    
    # Files and folders to include
    include_paths = [
        "src",
        "tests",
        "ci_workflow.yml",
        "local_ci_runner.py",
        "ci_build_report.json",
        "ci_documentation.md",
        "README.md",
        "WEEK6_FULL_SUBMISSION.md"
    ]
    
    print(f"Creating archive: {zip_filename}...")
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item in include_paths:
            full_path = os.path.join(script_dir, item)
            if not os.path.exists(full_path):
                print(f"  [Skipping missing path: {item}]")
                continue
            if os.path.isdir(full_path):
                for root, _, files in os.walk(full_path):
                    for file in files:
                        if file.endswith((".pyc", ".pyo")) or "__pycache__" in root:
                            continue
                        file_path = os.path.join(root, file)
                        archive_name = os.path.relpath(file_path, script_dir)
                        zipf.write(file_path, archive_name)
                        print(f"  + Added: {archive_name}")
            else:
                archive_name = os.path.relpath(full_path, script_dir)
                zipf.write(full_path, archive_name)
                print(f"  + Added: {archive_name}")

    file_size_kb = os.path.getsize(zip_filename) / 1024.0
    print(f"\n[SUCCESS] Archive generated successfully: {zip_filename} ({file_size_kb:.2f} KB)")

if __name__ == "__main__":
    package_week6()

