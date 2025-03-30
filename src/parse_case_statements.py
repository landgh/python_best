import re

from case_to_dict import parse_condition_to_combos, print_combinations_table

# from case_to_dict import parse_condition_to_combos, print_combinations_table

# === Include the previously defined functions ===
# - parse_condition_to_combos()
# - print_combinations_table()
# from previous logic

# Reuse them, assuming they’re already in your codebase.

# --- Add this new function ---

def parse_case_statement(case_str):
    # Normalize and strip
    case_str = case_str.strip().lower()
    assert case_str.startswith("case"), "Must start with CASE"
    assert "end" in case_str, "Missing END"

    # Extract 'as output_column'
    match_alias = re.search(r'end\s+as\s+(\w+)', case_str)
    output_col = match_alias.group(1) if match_alias else "output"

    # Strip 'case' and 'end as output_col'
    body = case_str[4:match_alias.start()].strip()

    # Split into WHEN ... THEN ... blocks
    when_blocks = re.findall(r'when\s+(.*?)\s+then\s+(.*?)(?=\s+when|\s+else|\s*$)', body, re.DOTALL)
    else_match = re.search(r'else\s+(.*)', body)

    all_combos = []
    all_cols = set()
    for condition, then_val in when_blocks:
        then_val = then_val.strip().strip("'\"")
        combos, col_order = parse_condition_to_combos(condition)
        for c in combos:
            c["direct mapped"] = then_val
            c[output_col] = then_val
            all_cols.update(c.keys())
        all_combos.extend(combos)

    # Handle ELSE block with wildcard "*"
    if else_match:
        else_val = else_match.group(1).strip().strip("'\"")
        wildcard_row = {k: '*' for k in all_cols if k not in ("direct mapped", output_col)}
        wildcard_row["direct mapped"] = else_val
        wildcard_row[output_col] = else_val
        all_combos.append(wildcard_row)

    # Make a nice column order
    final_cols = sorted(all_cols - {"direct mapped", output_col})
    final_cols += ["direct mapped", output_col]

    print_combinations_table(all_combos, final_cols)

# === Usage Example ===
# input_case = """
# case 
#   when c1 = 'v1' and c2 = 'v2' then 'mapped1'
#   when c1 = 'v3' or c2 = 'v4' then 'mapped2'
#   else 'default_val' 
# end as output_column
# """

input_case = """
case 
  when age >= 30 and salary < 5000 then 'tier1'
  when age < 30 or salary >= 10000 then 'tier2'
  when c <= date('2023-01-01') then 'past'
  when c > now() then 'future'
  else 'other'
end as tier
"""

parse_case_statement(input_case)