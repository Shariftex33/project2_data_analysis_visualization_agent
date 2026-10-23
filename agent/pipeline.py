
from __future__ import annotations
from pathlib import Path
import pandas as pd
from .data_engine import profile_dataset, automatic_eda, dataframe_preview, safe_eval_pandas
from .llm import LLMClient, build_analysis_prompt, extract_json
from .visualizer import make_chart

class DataAnalysisAgent:
    def __init__(self, llm: LLMClient, chart_dir="charts"):
        self.llm = llm
        self.chart_dir = Path(chart_dir)

    def inspect(self, df):
        return profile_dataset(df), automatic_eda(df), dataframe_preview(df)

    def answer(self, df, question):
        profile, eda, preview = self.inspect(df)
        prompt = build_analysis_prompt(profile, eda, preview, question)
        raw = self.llm.chat(
            "You are a careful data analyst. Follow the requested JSON schema exactly.",
            prompt
        )
        plan = extract_json(raw)
        expression = plan.get("expression", "df.head(10)")
        try:
            result = safe_eval_pandas(df, expression)
        except Exception as exc:
            # One repair attempt, still restricted to a pandas expression.
            repair = self.llm.chat(
                "Repair the pandas expression. Return ONLY JSON: {\"expression\":\"...\"}. "
                "Use only df, pd, np and exact column names.",
                f"Expression: {expression}\nError: {exc}\nColumns: {list(df.columns)}"
            )
            repaired = extract_json(repair)
            expression = repaired.get("expression", "df.head(10)")
            result = safe_eval_pandas(df, expression)

        chart_path = None
        if plan.get("answer_type") == "chart" or plan.get("chart", {}).get("type") != "none":
            chart_path = self.chart_dir / "latest_analysis.png"
            make_chart(result, plan.get("chart", {}), chart_path)

        return {
            "plan": plan,
            "expression": expression,
            "result": result,
            "chart_path": str(chart_path) if chart_path else None,
            "profile": profile,
            "eda": eda
        }
