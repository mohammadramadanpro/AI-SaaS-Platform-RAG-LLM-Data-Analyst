"""Safe execution of LLM-generated pandas code."""

import ast
import re

import pandas as pd
import numpy as np

ALLOWED_MODULES = {"pandas", "numpy", "matplotlib", "plotly", "plotly.express", "math"}
BLOCKED_BUILTINS = {
    "exec", "eval", "compile", "__import__", "open", "input",
    "breakpoint", "exit", "quit", "globals", "locals",
}


def extract_code_block(text: str) -> str:
    """Extract Python code from markdown fences."""
    match = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def validate_code(code: str) -> tuple[bool, str]:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax error: {e}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_MODULES:
                    return False, f"Import not allowed: {alias.name}"
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] not in ALLOWED_MODULES:
                return False, f"Import not allowed: {node.module}"
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_BUILTINS:
                return False, f"Blocked function: {node.func.id}"

    return True, "OK"


def execute_code(code: str, df: pd.DataFrame, charts_dir: str = "charts") -> dict:
    safe, msg = validate_code(code)
    if not safe:
        return {"error": msg}

    import plotly.express as px
    import plotly.graph_objects as go

    namespace = {
        "df": df.copy(),
        "pd": pd,
        "np": np,
        "px": px,
        "go": go,
        "charts_dir": charts_dir,
    }

    try:
        exec(code, {"__builtins__": {}}, namespace)
        result = namespace.get("result", "No result variable found.")
        chart = namespace.get("chart_path")
        return {
            "result": str(result) if not isinstance(result, pd.DataFrame) else result.to_string(),
            "chart": chart,
        }
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def get_data_summary(df: pd.DataFrame) -> str:
    return f"""Dataset Info:
- Shape: {df.shape[0]} rows x {df.shape[1]} columns
- Columns: {list(df.columns)}
- Data types:
{df.dtypes.to_string()}
- Sample (first 3 rows):
{df.head(3).to_string()}
- Numeric summary:
{df.describe().to_string()}
- Null counts:
{df.isnull().sum().to_string()}"""
