from datetime import datetime

import os
from pathlib import Path

def generate_readme(py_file_path: str):
    py_file = Path(py_file_path)
    if not py_file.is_file():
        raise FileNotFoundError(f"Python file '{py_file_path}' not found.")

    with py_file.open("r", encoding="utf-8") as f:
        code = f.read()

    title = py_file.stem
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = f"README_{title}.md"

    readme_content = f"""# {title}

This module is a Python script that includes functionality related to workflows, event-driven triggers, and singleton management via `WorkflowManager`.

## 🔍 Overview

This test suite verifies:

- Workflow creation and state transitions
- Event triggering behavior
- Singleton enforcement for `WorkflowManager`
- Batch triggering of workflows

## ▶️ Usage

To run tests:

```bash
pytest {py_file.name} -v

{code}

"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"✅ README.md successfully generated for: {py_file_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate README.md from Python file.")
    parser.add_argument("py_file", help="Path to the Python file to document")
    parser.add_argument("--output", default="README.md", help="Output path for README.md")

    args = parser.parse_args()

    generate_readme(args.py_file)