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
            @?[\w.]+                 # identifiers with optional @ for sql param (column names, values)
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
            # After an operator, capture full expression like: date('2023-01-01') or now()
            val_parts = []
            parens = 0
            while True:
                tok = peek()
                if tok is None:
                    break
                if tok.lower() in ('and', 'or') and parens == 0:
                    break
                if tok == '(':
                    parens += 1
                elif tok == ')':
                    if parens == 0:
                        break
                    parens -= 1
                val_parts.append(consume())
            val_expr = ' '.join(val_parts)
            # Clean quotes, or keep as raw expression
            val = val_expr.strip()
            if op == '=':
                return [{col: val}]
            else:
                return [{col: f"{op} {val}"}]

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
