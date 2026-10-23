
from __future__ import annotations
import json, os, re
from typing import Dict, Any, Optional

class LLMClient:
    def __init__(self, provider="ollama", model="qwen2.5:3b", base_url="http://localhost:11434", api_key=None):
        self.provider = provider.lower()
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def chat(self, system: str, user: str) -> str:
        if self.provider == "ollama":
            return self._ollama(system, user)
        if self.provider == "openai":
            return self._openai(system, user)
        raise ValueError(f"Unknown provider: {self.provider}")

    def _ollama(self, system, user):
        import requests
        r = requests.post(
            f"{self.base_url}/api/chat",
            json={"model": self.model,
                  "messages":[{"role":"system","content":system},{"role":"user","content":user}],
                  "stream": False,
                  "options":{"temperature":0.1}},
            timeout=180
        )
        r.raise_for_status()
        return r.json()["message"]["content"]

    def _openai(self, system, user):
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            messages=[{"role":"system","content":system},{"role":"user","content":user}]
        )
        return response.choices[0].message.content

def extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise ValueError("LLM did not return valid JSON.")
        return json.loads(match.group(0))

def build_analysis_prompt(profile, eda, preview, question):
    return f"""
You are a data-analysis planning agent. You are NOT allowed to invent columns.
Dataset profile:
{json.dumps(profile, indent=2)}

EDA highlights:
{json.dumps(eda, indent=2, default=str)[:12000]}

Sample rows:
{json.dumps(preview, indent=2, default=str)[:8000]}

User request:
{question}

Return ONLY valid JSON with:
{{
  "answer_type": "table|number|text|chart",
  "expression": "one safe pandas expression using only df, pd, np",
  "chart": {{
      "type": "bar|line|scatter|hist|box|none",
      "x": "column or null",
      "y": "column or null",
      "aggregation": "mean|sum|count|median|none",
      "title": "short chart title"
  }},
  "explanation": "what the result means and what to look for",
  "insight_focus": "one concise analytical focus"
}}

Rules:
- Use exact column names from the profile.
- For grouped summaries, prefer pandas expressions such as
  df.groupby('region', dropna=False)['sales'].mean().sort_values(ascending=False)
- For overall values use expressions such as df['sales'].mean().
- For a chart, the expression should normally produce a Series/DataFrame.
- If the question is ambiguous, set answer_type to "text", expression to "df.head(10)",
  and explain what clarification is needed.
"""
