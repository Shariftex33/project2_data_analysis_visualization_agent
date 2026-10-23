
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def make_chart(result, chart_spec, output_path: Path):
    chart_type = chart_spec.get("type", "none")
    if chart_type == "none":
        return None
    title = chart_spec.get("title") or "Analysis"
    x = chart_spec.get("x")
    y = chart_spec.get("y")
    fig, ax = plt.subplots(figsize=(9, 5.2))

    if isinstance(result, pd.Series):
        s = result
        if chart_type == "bar":
            s.plot(kind="bar", ax=ax)
        elif chart_type == "line":
            s.plot(kind="line", marker="o", ax=ax)
        elif chart_type == "hist":
            s.plot(kind="hist", bins=20, ax=ax)
        elif chart_type == "box":
            s.plot(kind="box", ax=ax)
        else:
            s.plot(kind="bar", ax=ax)
    elif isinstance(result, pd.DataFrame):
        plot_df = result.copy()
        if chart_type in ("bar", "line") and x and y and x in plot_df.columns and y in plot_df.columns:
            plot_df.plot(kind=chart_type, x=x, y=y, ax=ax, legend=False, marker="o" if chart_type=="line" else None)
        elif chart_type == "scatter" and x in plot_df.columns and y in plot_df.columns:
            plot_df.plot.scatter(x=x, y=y, ax=ax)
        elif chart_type == "hist":
            numeric = plot_df.select_dtypes(include=np.number)
            if not numeric.empty:
                numeric.iloc[:, 0].plot(kind="hist", bins=20, ax=ax)
        elif chart_type == "box":
            numeric = plot_df.select_dtypes(include=np.number)
            if not numeric.empty:
                numeric.iloc[:, :5].plot(kind="box", ax=ax)
        else:
            numeric = plot_df.select_dtypes(include=np.number)
            if not numeric.empty:
                numeric.iloc[:, :3].plot(kind="bar", ax=ax)
    else:
        raise ValueError("Chart result must be a Series or DataFrame.")

    ax.set_title(title)
    ax.set_xlabel(x or "")
    ax.set_ylabel(y or "Value")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return output_path
