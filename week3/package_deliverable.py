import zipfile
import os

def package_week3():
    files_to_include = [
        "models.py",
        "module_logic.py",
        "test_suite.py",
        "test_documentation.md",
        "WEEK3_FULL_SUBMISSION.md",
        "README.md",
        "task.md"
    ]

    output_filename = "week3_deliverable.zip"

    print(f"Creating {output_filename}...")
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_include:
            if os.path.exists(file):
                zipf.write(file)
                print(f"Added: {file}")
            else:
                print(f"Warning: {file} not found, skipping.")

    size_kb = os.path.getsize(output_filename) / 1024
    print(f"\nSuccessfully created {output_filename}! ({size_kb:.2f} KB)")

if __name__ == "__main__":
    package_week3()
