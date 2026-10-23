# Demo Script

## Demo 1 — Sales

Upload `data/sample_sales.csv`.

Ask:

> What is the average sales by region?

Expected workflow:
1. Dataset is profiled.
2. LLM chooses a group-by mean operation.
3. Restricted Pandas expression is executed.
4. Bar chart is generated.
5. Agent explains the result.

## Demo 2 — Yarn quality

Upload `data/sample_yarn_quality.csv`.

Ask:

> Show the relationship between twist and hairiness.

Expected workflow:
1. LLM identifies `twist_tpm` and `hairiness`.
2. It selects a scatter visualization.
3. Matplotlib generates the chart.
4. The interface displays the result and explanation.

## Model switch

In the sidebar:
- Start with `qwen2.5:3b`
- Switch to `gemma3:4b`
- If available, test `gpt-oss:120b-cloud`
- Or switch to OpenAI API mode

The data-processing and visualization pipeline remains the same.
