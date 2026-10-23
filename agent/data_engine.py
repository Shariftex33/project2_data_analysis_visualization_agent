
from __future__ import annotations
import io, json, re, traceback
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
import numpy as np

MAX_ROWS = 200_000
MAX_COLS = 200

def load_dataset(uploaded_file) -> pd.DataFrame:
    name = getattr(uploaded_file, "name", "").lower()
    if name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file type. Please upload CSV or Excel.")
    if df.empty:
        raise ValueError("The dataset is empty.")
    if len(df) > MAX_ROWS:
        raise ValueError(f"Dataset has {len(df):,} rows; limit is {MAX_ROWS:,}.")
    if len(df.columns) > MAX_COLS:
        raise ValueError(f"Dataset has {len(df.columns)} columns; limit is {MAX_COLS}.")
    # Normalize duplicate column names without changing the original meaning.
    df = df.copy()
    df.columns = make_unique_columns([str(c).strip() for c in df.columns])
    return df

def make_unique_columns(columns):
    seen = {}
    result = []
    for c in columns:
        base = c or "unnamed"
        seen[base] = seen.get(base, 0) + 1
        result.append(base if seen[base] == 1 else f"{base}_{seen[base]}")
    return result

def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    numeric = df.select_dtypes(include=np.number).columns.tolist()
    categorical = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    datetime_cols = []
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            datetime_cols.append(c)
    missing = df.isna().sum()
    profile = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "memory_mb": round(df.memory_usage(deep=True).sum()/1024**2, 2),
        "numeric_columns": numeric,
        "categorical_columns": categorical,
        "datetime_columns": datetime_cols,
        "missing_total": int(missing.sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns_detail": []
    }
    for c in df.columns:
        profile["columns_detail"].append({
            "name": c,
            "dtype": str(df[c].dtype),
            "missing": int(df[c].isna().sum()),
            "missing_pct": round(float(df[c].isna().mean()*100), 2),
            "unique": int(df[c].nunique(dropna=True))
        })
    return profile

def automatic_eda(df: pd.DataFrame) -> Dict[str, Any]:
    desc = df.describe(include="all").transpose()
    desc = desc.replace({np.nan: None})
    correlations = df.select_dtypes(include=np.number).corr(numeric_only=True)
    top_correlations = []
    if not correlations.empty:
        cols = correlations.columns
        for i, a in enumerate(cols):
            for j, b in enumerate(cols):
                if j > i and pd.notna(correlations.loc[a,b]):
                    top_correlations.append((a,b,float(correlations.loc[a,b])))
        top_correlations.sort(key=lambda x: abs(x[2]), reverse=True)
    return {
        "summary": desc.reset_index().to_dict(orient="records"),
        "top_correlations": top_correlations[:10],
        "numeric_means": df.select_dtypes(include=np.number).mean(numeric_only=True).round(4).to_dict(),
        "numeric_medians": df.select_dtypes(include=np.number).median(numeric_only=True).round(4).to_dict()
    }

def safe_eval_pandas(df: pd.DataFrame, expression: str):
    """
    Evaluate a deliberately restricted pandas expression.
    This is NOT a general Python REPL. It permits only dataframe-oriented
    expressions using df and selected pandas/numpy functions.
    """
    expression = expression.strip().strip("`")
    if len(expression) > 1200:
        raise ValueError("Generated expression is too long.")
    forbidden = [
        "__", "import ", "open(", "exec(", "eval(", "compile(", "os.",
        "sys.", "subprocess", "shutil", "pathlib", "socket", "requests",
        "urllib", "builtins", "globals(", "locals(", "getattr(", "setattr("
    ]
    low = expression.lower()
    if any(x in low for x in forbidden):
        raise ValueError("Unsafe expression rejected.")
    allowed_names = {
        "df": df,
        "pd": pd,
        "np": np,
    }
    result = eval(expression, {"__builtins__": {}}, allowed_names)
    if isinstance(result, pd.DataFrame):
        return result.head(1000)
    if isinstance(result, pd.Series):
        return result.head(1000)
    if isinstance(result, (np.generic,)):
        return result.item()
    return result

def dataframe_preview(df, n=10):
    return df.head(n).to_dict(orient="records")
