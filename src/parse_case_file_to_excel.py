import re
import pandas as pd
from typing import Dict

from parse_case_statements import parse_case_statement

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

    # print(f"Loaded rules: {rules}")
    all_dataframes = {}

    # First pass: parse and collect all combos + headers
    for key, case_str in rules.items():
        # parsed = parse_single_case(case_str)  # <- Replace with your real parser
        # df = pd.DataFrame(parsed['combos'])
        data = parse_case_statement(case_str)
        df = pd.DataFrame(data)
        all_dataframes[key] = df

    # Standardized column order
    common_columns = [
            "c", "c1", "c2", "age", "salary",         # your expected input columns
            "output_column"  # always include these for output
        ]

    # print(all_dataframes)
    
    # Write to Excel with consistent headers
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for sheet_name, df in all_dataframes.items():
            # Step 1: Rename the actual output column to "output_column"
            for col in df.columns:
                if col not in common_columns and col != "direct mapped":
                    df["output_column"] = df[col]
                    df.drop(columns=[col], inplace=True)
                    break  # we found the output column

            # Step 2: Reindex using your fixed header list
            df_out = df.reindex(columns=common_columns, fill_value="")
            df_out.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            # print(df_out)

    print(f"✅ Written to {output_file} with consistent columns across sheets.")


if __name__ == "__main__":
    parse_case_file_to_excel('resources/case_statements.txt', 'case_statements.xlsx')