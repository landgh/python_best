import re

from case_to_dict import parse_condition_to_combos, print_combinations_table

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

    return all_combos