import re
import itertools
from typing import List, Dict, Any, Union

# ----------- Tokenizer ------------ #

def tokenize(expression: str) -> List[str]:
    token_pattern = re.compile(r"""
        \s*(=>|==|!=|<=|>=|[()=,]|\bin\b|\band\b|\bor\b|then|'[^']*'|[a-zA-Z_]\w*)\s*
    """, re.IGNORECASE | re.VERBOSE)
    tokens = token_pattern.findall(expression)
    return [t.strip() for t in tokens if t.strip()]

# ----------- AST Parsing ------------ #

class ExprNode:
    pass

class AndNode(ExprNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        self.left = left
        self.right = right

class OrNode(ExprNode):
    def __init__(self, left: ExprNode, right: ExprNode):
        self.left = left
        self.right = right

class ConditionNode(ExprNode):
    def __init__(self, column: str, operator: str, values: List[str]):
        self.column = column
        self.operator = operator
        self.values = values

# Recursive descent parser
def parse_expression(tokens: List[str]) -> ExprNode:
    def parse_primary(index):
        if tokens[index] == '(':
            expr, next_index = parse_logic(index + 1)
            if tokens[next_index] != ')':
                raise SyntaxError("Expected ')'")
            return expr, next_index + 1
        else:
            return parse_condition(index)

    def parse_condition(index):
        column = normalize_column_name(tokens[index])
        # column = tokens[index]
        op = tokens[index + 1].lower()
        values = []

        if op == '=':
            values = [tokens[index + 2].strip("'")]
            return ConditionNode(column, '=', values), index + 3

        elif op == 'in':
            if tokens[index + 2] != '(':
                raise SyntaxError("Expected '(' after IN")
            i = index + 3
            while tokens[i] != ')':
                if tokens[i] != ',':
                    values.append(tokens[i].strip("'"))
                i += 1
            return ConditionNode(column, 'in', values), i + 1
        else:
            raise SyntaxError(f"Unsupported operator: {op}")

    def parse_logic(index):
        left, index = parse_primary(index)

        while index < len(tokens):
            op = tokens[index].lower()
            if op == 'and':
                right, index = parse_primary(index + 1)
                left = AndNode(left, right)
            elif op == 'or':
                right, index = parse_primary(index + 1)
                left = OrNode(left, right)
            else:
                break
        return left, index

    ast, _ = parse_logic(0)
    return ast

# ----------- Evaluator ------------ #

def evaluate_ast(node: ExprNode) -> List[Dict[str, str]]:
    if isinstance(node, ConditionNode):
        return [{node.column: v} for v in node.values]

    elif isinstance(node, AndNode):
        left = evaluate_ast(node.left)
        right = evaluate_ast(node.right)
        result = []
        for l, r in itertools.product(left, right):
            combined = l.copy()
            combined.update(r)
            result.append(combined)
        return result

    elif isinstance(node, OrNode):
        left = evaluate_ast(node.left)
        right = evaluate_ast(node.right)
        return left + right

    else:
        raise ValueError("Unknown AST node")

# ----------- Main Function ------------ #

def parse_condition_string(input_str: str) -> List[Dict[str, str]]:
    # Extract 'then' clause
    then_match = re.search(r"\bthen\s+'?([^']+)'?", input_str, re.IGNORECASE)
    then_value = then_match.group(1) if then_match else None
    condition_part = re.sub(r"\bthen\s+'?([^']+)'?", '', input_str, flags=re.IGNORECASE)

    tokens = tokenize(condition_part)
    ast = parse_expression(tokens)
    rows = evaluate_ast(ast)

    if then_value:
        for row in rows:
            row['direct mapped'] = then_value

    return rows

def normalize_column_name(col: str) -> str:
    return col.split('.')[-1] if '.' in col else col


def print_as_table(dict_list: List[Dict[str, str]]):
    if not dict_list:
        print("No data to display.")
        return

    # Collect all unique keys across rows to ensure consistent columns
    all_keys = sorted(set().union(*(d.keys() for d in dict_list)))

    # Print header
    print('\t'.join(all_keys))

    # Print each row of values
    for row in dict_list:
        print('\t'.join(row.get(k, '') for k in all_keys))



# ----------- Example ------------ #

input_str = """
    c1 in ('v1', 'v2') and (c2 = 'v3' or (trd.c2 = 'v4' and c4 = 'v6')) and c3 = 'v5' then 'mapped_value'
"""

parsed = parse_condition_string(input_str)
print_as_table(parsed)