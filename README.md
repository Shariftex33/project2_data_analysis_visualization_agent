# Project 2 — Data Analysis & Visualization Agent

An AI-powered data-analysis agent that accepts CSV/Excel datasets, automatically explores their structure, performs EDA, answers natural-language questions, generates visualizations, and explains the results.

## 1. Features

- CSV / Excel upload
- Automatic column/type/missing-value/duplicate detection
- Automatic EDA and numeric correlations
- Natural-language data questions
- LLM-generated **restricted Pandas expressions**
- Dynamic Matplotlib charts
- Written explanations and analytical focus
- Error handling + one repair attempt
- Local Ollama models and OpenAI API mode
- Two sample datasets
- Unit tests
- Streamlit UI

## 2. Architecture

```text
                 ┌─────────────────────┐
CSV / Excel ───► │ Streamlit interface │
                 └──────────┬──────────┘
                            │
                    profile + EDA
                            │
                            ▼
                 ┌─────────────────────┐
                 │   Analysis Agent    │
                 │                     │
                 │ LLM → JSON plan    │
                 │        │            │
                 │        ▼            │
                 │ Restricted Pandas   │
                 │ execution           │
                 └──────┬───────┬──────┘
                        │       │
                     result    chart
                        │       │
                        └───┬───┘
                            ▼
                  Answer + visualization
                     + explanation
```

### Model options

The sidebar supports:

**Local Ollama**

- `qwen2.5:3b` — recommended for your laptop
- `gemma3:4b`
- `gpt-oss:120b-cloud` — if your Ollama installation/account supports this model

**OpenAI API**

- Any OpenAI chat model available to your API account; enter the model name in the sidebar.

The application does not require OpenAI when using Ollama.

## 3. Installation

### Windows PowerShell

```powershell
cd project2_data_analysis_visualization_agent

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Local Ollama

Install/start Ollama and make sure the selected model exists.

Example:

```powershell
ollama list
ollama pull qwen2.5:3b
```

Then test:

```powershell
ollama run qwen2.5:3b
```

Keep Ollama running while the Streamlit application is open.

## 4. Run

```powershell
streamlit run app/streamlit_app.py
```

Open the Streamlit address shown in the terminal, normally:

```text
http://localhost:8501
```

## 5. OpenAI API mode

Copy `.env.example` to `.env` or set the variable in PowerShell:

```powershell
$env:OPENAI_API_KEY="your-key"
```

Then start Streamlit and select **OpenAI API** in the sidebar.

## 6. Sample datasets

### `data/sample_sales.csv`

A synthetic retail/textile sales dataset with:

- date
- region
- category
- units sold
- unit price
- discount
- sales
- profit

Example questions:

- What is the average sales by region?
- Which category has the highest profit?
- Show sales by month.
- Which region has the highest average profit?

### `data/sample_yarn_quality.csv`

A synthetic textile-yarn quality dataset with:

- yarn count
- twist
- hairiness
- CV%
- strength
- elongation
- machine

Example questions:

- What is the average hairiness by machine?
- Is twist related to hairiness?
- Which machine has the lowest CV%?
- Show the relationship between twist and hairiness.

## 7. Safety design

Instead of exposing a general-purpose Python REPL to the LLM, the project uses a restricted Pandas expression evaluator.

Rejected examples include:

- `__import__`
- `open()`
- `os`
- `subprocess`
- `requests`
- arbitrary `eval/exec`
- filesystem/network operations

The LLM therefore proposes a dataframe operation, but the application validates the expression before execution.

This is safer and easier to explain during the presentation than unrestricted Python execution.

## 8. Project structure

```text
project2_data_analysis_visualization_agent/
│
├── app/
│   └── streamlit_app.py
│
├── agent/
│   ├── __init__.py
│   ├── data_engine.py
│   ├── llm.py
│   ├── pipeline.py
│   └── visualizer.py
│
├── data/
│   ├── sample_sales.csv
│   └── sample_yarn_quality.csv
│
├── charts/
│   ├── sales_by_region.png
│   └── yarn_twist_hairiness.png
│
├── presentation/
│   └── Project_2_Data_Analysis_Agent.pptx
│
├── tests/
│   └── test_data_engine.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 9. Testing

```powershell
pytest -q
```

## 10. Suggested 5–7 minute demo

1. Upload `sample_sales.csv`.
2. Show automatic structure detection.
3. Show missing values and EDA.
4. Ask: **What is the average sales by region?**
5. Show generated table/chart/explanation.
6. Upload `sample_yarn_quality.csv`.
7. Ask: **Show the relationship between twist and hairiness.**
8. Switch from local `qwen2.5:3b` to another available model.
9. Explain the safety layer and architecture.

## 11. Learning outcomes demonstrated

| Assignment objective        | Implementation               |
| --------------------------- | ---------------------------- |
| Structured data interaction | Pandas data engine           |
| Code execution as a tool    | Restricted Pandas evaluator  |
| Dynamic visualization       | Matplotlib chart generator   |
| LLM-driven analysis         | JSON analysis plan           |
| Natural language questions  | Streamlit + LLM              |
| Error handling              | Validation + repair attempt  |
| Safe execution              | Blocked dangerous operations |
| Practical UI                | Streamlit                    |

## 12. Important note

This project intentionally does not use LangChain's unrestricted `PythonREPL` by default. The assignment lists LangChain as a suggested technology, not a mandatory requirement. The direct Python/Pandas architecture is smaller, easier to understand, and provides a clearer safety boundary for a student project.
