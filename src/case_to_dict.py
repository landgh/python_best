import re
import itertools

def parse_conditions_with_then(condition_str):
    # Extract the THEN value if it exists
    then_match = re.search(r"\bthen\s+'?([^']+)'?", condition_str, re.IGNORECASE)
    then_value = then_match.group(1) if then_match else None

    # Remove the THEN clause from the condition string
    condition_clean = re.sub(r"\bthen\s+'?([^']+)'?", '', condition_str, flags=re.IGNORECASE)

    # Patterns to match `col IN (...)` and `col = 'value'`
    in_pattern = re.compile(r"(\w+)\s+in\s+\(([^)]+)\)", re.IGNORECASE)
    eq_pattern = re.compile(r"(\w+)\s*=\s*'([^']*)'")

    # Parse the conditions
    in_clauses = in_pattern.findall(condition_clean)
    eq_clauses = eq_pattern.findall(condition_clean)

    # Build a dict of column -> list of values
    values_map = {}

    for col, vals in in_clauses:
        items = [v.strip().strip("'") for v in vals.split(',')]
        values_map[col] = items

    for col, val in eq_clauses:
        if col not in values_map:  # Avoid overwriting IN clauses
            values_map[col] = [val]

    # Cartesian product of all value combinations
    keys = list(values_map.keys())
    value_combinations = itertools.product(*(values_map[k] for k in keys))
    result = [dict(zip(keys, combo)) for combo in value_combinations]

    # Add "direct mapped": <then_value> if applicable
    if then_value is not None:
        for row in result:
            row["direct mapped"] = then_value

    return result

# Example usage
input_str = "c1 in ('v1', 'v2') and c2 = 'v3' and c3 = 'v4' and c4 in ('v6', 'v7') then 'v5'"
parsed = parse_conditions_with_then(input_str)
for i, row in enumerate(parsed, 1):
    print(f"{i}: {row}")
