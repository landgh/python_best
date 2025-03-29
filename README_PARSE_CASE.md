###  paser_case_statement.py
```python

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
  else 'other'
end as tier
"""

parse_case_statement(input_case)
```

### case_to_dict.py
```python

def normalize_column_name(col: str) -> str:
    return col.split('.')[-1]

def parse_condition_to_combos(condition_str):
    import re
    # Tokenization pattern: catches multi-char operators, words, strings, symbols
    token_pattern = re.compile(r"""
        \s*(
            <=|>=|!=|<>|=|<|>|      # comparison operators
            \bAND\b|\bOR\b|\bIN\b| # logic keywords
            \(|\)|,|               # symbols
            '[^']*'|               # quoted string
            [\w.]+                 # identifiers (column names, values)
        )\s*
    """, re.IGNORECASE | re.VERBOSE)
    
    tokens = token_pattern.findall(condition_str)
    tokens = [t.strip() for t in tokens if t.strip()]
    
    index = 0
    col_order = []

    def peek():
        return tokens[index] if index < len(tokens) else None

    def consume(expected=None):
        nonlocal index
        tok = peek()
        if tok and (expected is None or tok.lower() == expected.lower()):
            index += 1
            return tok
        return None

    def parse_value_token(val_tok):
        val = val_tok
        if val.startswith("'") and val.endswith("'"):
            return val[1:-1]
        try:
            return str(int(val))
        except ValueError:
            try:
                return str(float(val))
            except ValueError:
                return val

    def parse_condition():
        col_token = consume()
        col = normalize_column_name(col_token)
        if col not in col_order:
            col_order.append(col)
        op = consume()
        op_map = {'<>': '!='}  # normalize <>
        if op in op_map:
            op = op_map[op]
        if op.lower() == 'in':
            consume('(')
            values = []
            while True:
                val_tok = consume()
                if val_tok in [')', None]:
                    break
                if val_tok != ',':
                    val = parse_value_token(val_tok)
                    values.append({col: val})
            return values
        else:
            val_tok = consume()
            val = parse_value_token(val_tok)
            if op == '=':
                return [{col: val}]
            else:
                return [{col: f"{op}{val}"}]

    def parse_factor():
        if peek() == '(':
            consume('(')
            res = parse_or()
            consume(')')
            return res
        else:
            return parse_condition()

    def merge_and(left, right):
        merged = []
        for l in left:
            for r in right:
                combo = l.copy()
                conflict = False
                for k, v in r.items():
                    if k in combo and combo[k] != v:
                        conflict = True
                        break
                    combo[k] = v
                if not conflict:
                    merged.append(combo)
        return merged

    def parse_and():
        res = parse_factor()
        while peek() and peek().lower() == 'and':
            consume('and')
            right = parse_factor()
            res = merge_and(res, right)
        return res

    def parse_or():
        res = parse_and()
        while peek() and peek().lower() == 'or':
            consume('or')
            right = parse_and()
            res.extend(right)
        return res

    combos = parse_or()
    return combos, col_order

def print_combinations_table(combos, col_order):
    """Print the list of combination dictionaries as a table with given column order."""
    if not combos:
        return
    # Ensure "direct mapped" is the last column in order
    if "direct mapped" in combos[0] and "direct mapped" not in col_order:
        col_order.append("direct mapped")
    # Determine column widths for pretty alignment
    widths = {col: len(col) for col in col_order}
    for combo in combos:
        for col in col_order:
            val_str = str(combo.get(col, ""))
            widths[col] = max(widths[col], len(val_str))
    # Print header
    header = " | ".join(col.ljust(widths[col]) for col in col_order)
    separator = "-+-".join("-" * widths[col] for col in col_order)
    print(header)
    print(separator)
    # Print each row
    for combo in combos:
        row = []
        for col in col_order:
            value = str(combo.get(col, ""))
            row.append(value.ljust(widths[col]))
        print(" | ".join(row))

```
