import re
import pandas as pd
from typing import Dict

# -- Helper: Parse multi-line case statements with key as sheet name --
def load_rules_from_file(filepath: str) -> Dict[str, str]:
    rules = {}
    current_key = None
    buffer = []

    with open(filepath, 'r') as f:
        for line in f:
            stripped = line.strip()

            # Detect a key line (like "my_key_1:")
            if re.match(r'^\w[\w\d_]*\s*:$', stripped):
                if current_key and buffer:
                    rules[current_key] = '\n'.join(buffer).strip()
                    buffer = []
                current_key = stripped.rstrip(':').strip()
            else:
                if current_key:
                    buffer.append(line.rstrip())

        if current_key and buffer:
            rules[current_key] = '\n'.join(buffer).strip()

    return rules

# -- Dummy parser to simulate the parse_single_case + parse_condition_to_combos logic --
def fake_parse_case_to_combos(case_str: str):
    # This is a simplified placeholder for demonstration
    # You should replace this with your full `parse_single_case` logic
    return [
        {"example_column": "val1", "direct mapped": "mapped_val", "output_column": "mapped_val"},
        {"example_column": "val2", "direct mapped": "mapped_val", "output_column": "mapped_val"}
    ]

# -- Write to Excel, each sheet named after the key --
def parse_case_file_to_excel(filepath: str, output_file: str):
    rules = load_rules_from_file(filepath)
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for key, case_str in rules.items():
            data = fake_parse_case_to_combos(case_str)
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=key[:31], index=False)
    return output_file

if __name__ == "__main__":
    parse_case_file_to_excel('resources/case_statements.txt', 'case_statements.xlsx')