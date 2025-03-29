###  paser_case_statement.py
```python
import re

from case_to_dict import parse_condition_to_combos, print_combinations_table

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
input_case = """
case 
  when c1 = 'v1' and c2 = 'v2' then 'mapped1'
  when c1 = 'v3' or c2 = 'v4' then 'mapped2'
  else 'default_val' 
end as output_column
"""

parse_case_statement(input_case)

```

### case_to_dict.py
```python
def parse_condition_to_combos(condition_str):
    """
    Parse a conditional expression (without the 'then' part) and return a list of dicts
    for all satisfying combinations of column values.
    """
    # Tokenize the condition string into identifiers, values, and operators
    tokens = []
    i = 0
    s = condition_str.strip()
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        if s[i] in ('(', ')', '=', ','):
            tokens.append(s[i])
            i += 1
        elif s[i:i+3].lower() == 'and' and (i+3 == len(s) or not s[i+3].isalnum()):
            tokens.append('and')
            i += 3
        elif s[i:i+2].lower() == 'or' and (i+2 == len(s) or not s[i+2].isalnum()):
            tokens.append('or')
            i += 2
        elif s[i:i+2].lower() == 'in' and (i+2 == len(s) or not s[i+2].isalnum()):
            tokens.append('in')
            i += 2
        elif s[i] in ("'", '"'):
            # Quoted value
            quote = s[i]
            i += 1
            start = i
            # Capture everything until the matching quote
            while i < len(s) and s[i] != quote:
                i += 1
            value = s[start:i]  # content inside quotes
            tokens.append(quote + value + quote)  # keep quotes as marker
            i += 1  # skip closing quote
        else:
            # Identifier (column or prefix.column or possibly an unquoted literal/number)
            start = i
            while i < len(s) and (s[i].isalnum() or s[i] in ('_', '.')):
                i += 1
            tokens.append(s[start:i])
    # Now we have a list of tokens to parse.
    
    # Parser index and functions for recursive descent
    index = 0
    def peek():
        return tokens[index] if index < len(tokens) else None
    def consume(expected=None):
        """Consume and return the next token (optionally verifying it matches an expected value)."""
        nonlocal index
        if index < len(tokens):
            tok = tokens[index]
            if expected is None or tok.lower() == expected.lower():
                index += 1
                return tok
        return None
    
    # We will also record the order of column names as they appear (without prefix) for output
    col_order = []
    
    def parse_factor():
        """Parse a factor: either a parenthesized sub-expression or a simple condition."""
        tok = peek()
        if tok == '(':
            consume('(')
            result = parse_or_expr()  # parse inside parentheses as a full expression
            consume(')')
            return result
        else:
            return parse_condition()
    
    def parse_condition():
        """Parse a simple condition of the form <col> = <val> or <col> in (<val1>, ...)."""
        # Parse column identifier (with possible prefix)
        tok = consume()  # column token
        if tok is None:
            return []  # error handling: no token where expected
        # If there's a prefix like "trd.c2", strip everything before the dot
        col_name = tok.split('.')[-1]  
        if col_name not in col_order:
            col_order.append(col_name)
        # Next token should be an operator
        op = consume()
        if op is None:
            return []
        op = op.lower()
        # Handle the 'in' operator
        if op == 'in':
            consume('(')  # consume the opening parenthesis
            combos = []
            # Collect all values inside the parentheses separated by commas
            while True:
                val_tok = consume()
                if val_tok is None or val_tok == ')':
                    break
                if val_tok == ',':
                    continue
                # Remove quotes from value token if present
                val = val_tok
                if len(val) >= 2 and ((val[0] == "'" and val[-1] == "'") or (val[0] == '"' and val[-1] == '"')):
                    val = val[1:-1]
                else:
                    # Convert numeric tokens to int/float if possible
                    if val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
                        val = int(val)
                    else:
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                combos.append({col_name: val})
                # After a value, expect either a comma or closing parenthesis
                if peek() == ')':
                    break
            consume(')')  # consume closing parenthesis
            return combos
        elif op == '=':
            # Handle equality operator
            val_tok = consume()
            if val_tok is None:
                return []
            # Remove quotes and convert numeric if needed
            val = val_tok
            if len(val) >= 2 and ((val[0] == "'" and val[-1] == "'") or (val[0] == '"' and val[-1] == '"')):
                val = val[1:-1]
            else:
                if val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
                    val = int(val)
                else:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
            return [{col_name: val}]
        else:
            # Other operators (>, <, !=, etc.) are not explicitly needed for this task
            return []
    
    def parse_and_expr():
        """Parse a series of factors joined by 'and'."""
        # Start with the first factor
        combos = parse_factor()
        while True:
            tok = peek()
            if tok is None or tok.lower() != 'and':
                break
            consume('and')
            # Parse the next factor after 'and'
            right_combos = parse_factor()
            # Compute the AND (intersection) of current combos with right_combos
            new_combos = []
            for combo in combos:
                for rcombo in right_combos:
                    # Attempt to merge two combo dictionaries
                    merged = combo.copy()
                    conflict = False
                    for key, val in rcombo.items():
                        if key in merged:
                            if merged[key] != val:
                                conflict = True
                                break  # conflicting assignment
                        else:
                            merged[key] = val
                    if not conflict:
                        new_combos.append(merged)
            combos = new_combos
            # If no combinations survive an AND, we can break early (no solution in this branch)
            if not combos:
                break
        return combos
    
    def parse_or_expr():
        """Parse a series of AND-expressions joined by 'or'."""
        combos = parse_and_expr()
        while True:
            tok = peek()
            if tok is None or tok.lower() != 'or':
                break
            consume('or')
            # Parse the next AND-expression after 'or'
            right_combos = parse_and_expr()
            # Compute the OR (union) of combos with right_combos
            # We need to avoid duplicate combinations in the union
            seen = {tuple(sorted(c.items())): c for c in combos}
            for rc in right_combos:
                key = tuple(sorted(rc.items()))
                if key not in seen:
                    combos.append(rc)
                    seen[key] = rc
        return combos
    
    # Parse the full condition (OR expression covers the whole grammar)
    return parse_or_expr(), col_order

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

# Example usage with the given input string:
input_str = """
c1 in ('v1', 'v2') and (pos.c2 = 'v3' or (trd.c2 = 'v4' and atlas.c4 = 'v6')) and c3 = 'v5' then 'mapped_value'
"""
# Split the input into condition part and output (after 'then')
condition_part, output_part = input_str.split(' then ')
output_value = output_part.strip().strip("'\"")  # remove quotes from the output value
# Parse condition and get all satisfying combinations
combos, col_order = parse_condition_to_combos(condition_part)
# Add the "direct mapped" output value to each combination
for combo in combos:
    combo["direct mapped"] = output_value
# Print the result in tabular format
print_combinations_table(combos, col_order)

```
