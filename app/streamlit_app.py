
import os, sys
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.data_engine import load_dataset, profile_dataset, automatic_eda
from agent.llm import LLMClient
from agent.pipeline import DataAnalysisAgent

st.set_page_config(page_title="Data Analysis & Visualization Agent", page_icon="📊", layout="wide")

st.title("📊 Data Analysis & Visualization Agent")
st.caption("Upload CSV/Excel → automatic profiling → EDA → natural-language analysis → charts → explanations")

with st.sidebar:
    st.header("Model")
    provider = st.selectbox("Provider", ["Ollama (local)", "OpenAI API"])
    if provider.startswith("Ollama"):
        model = st.selectbox(
            "Local model",
            ["qwen2.5:3b", "gemma3:4b", "gpt-oss:120b-cloud"],
            index=0,
            help="Make sure the selected model is available in Ollama."
        )
        base_url = st.text_input("Ollama URL", "http://localhost:11434")
        api_key = None
    else:
        model = st.text_input("OpenAI model", "gpt-5.6-mini")
        base_url = ""
        api_key = os.getenv("OPENAI_API_KEY")
        st.info("Set OPENAI_API_KEY in your environment before starting the app.")

    st.divider()
    st.markdown("**Safety:** generated analysis is restricted to dataframe expressions; arbitrary OS/network/file operations are rejected.")

uploaded = st.file_uploader("Upload a dataset", type=["csv", "xlsx", "xls"])

if uploaded is None:
    st.info("Try one of the sample datasets in the `data/` folder, or upload your own CSV/Excel file.")
    st.markdown("### Example questions")
    st.write("- What is the average sales by region?")
    st.write("- Which category has the highest profit?")
    st.write("- Show the relationship between twist and hairiness.")
    st.write("- What columns have missing values?")
    st.write("- Give me three actionable insights from this dataset.")
    st.stop()

try:
    df = load_dataset(uploaded)
except Exception as e:
    st.error(f"Could not load dataset: {e}")
    st.stop()

profile = profile_dataset(df)
eda = automatic_eda(df)

tab1, tab2, tab3 = st.tabs(["🔎 Dataset", "📈 Automatic EDA", "🤖 Ask the Agent"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{profile['rows']:,}")
    c2.metric("Columns", profile["columns"])
    c3.metric("Missing values", f"{profile['missing_total']:,}")
    c4.metric("Duplicate rows", f"{profile['duplicate_rows']:,}")
    st.subheader("Column structure")
    st.dataframe(pd.DataFrame(profile["columns_detail"]), use_container_width=True)
    st.subheader("Preview")
    st.dataframe(df.head(20), use_container_width=True)

with tab2:
    st.subheader("Numeric summary")
    st.dataframe(df.describe(include="all").transpose(), use_container_width=True)
    st.subheader("Top numeric correlations")
    corr_rows = [{"column_1": a, "column_2": b, "correlation": round(c, 3)} for a,b,c in eda["top_correlations"]]
    st.dataframe(pd.DataFrame(corr_rows), use_container_width=True)

with tab3:
    question = st.text_area("Ask a question about the dataset", placeholder="e.g. What is the average sales by region?")
    if st.button("Analyze", type="primary") and question.strip():
        try:
            client = LLMClient(
                provider="ollama" if provider.startswith("Ollama") else "openai",
                model=model,
                base_url=base_url,
                api_key=api_key
            )
            agent = DataAnalysisAgent(client, chart_dir=ROOT / "charts")
            with st.spinner("Analyzing the dataset..."):
                result = agent.answer(df, question)

            plan = result["plan"]
            st.subheader("Answer")
            value = result["result"]
            if isinstance(value, (pd.DataFrame, pd.Series)):
                st.dataframe(value, use_container_width=True)
            else:
                st.write(value)

            if result["chart_path"]:
                st.subheader("Visualization")
                st.image(result["chart_path"], use_container_width=True)

            st.subheader("Explanation")
            st.write(plan.get("explanation", "No explanation returned."))

            st.subheader("Agent reasoning output")
            st.json({
                "answer_type": plan.get("answer_type"),
                "expression": result["expression"],
                "chart": plan.get("chart")
            })
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.caption("Check the model connection, selected model name, dataset columns, or try a more specific question.")
