
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from agent.data_engine import profile_dataset, safe_eval_pandas

def test_profile():
    df = pd.DataFrame({"a":[1,2,None], "b":["x","y","x"]})
    p = profile_dataset(df)
    assert p["rows"] == 3
    assert p["missing_total"] == 1

def test_safe_expression():
    df = pd.DataFrame({"sales":[10,20,30], "region":["A","A","B"]})
    result = safe_eval_pandas(df, "df.groupby('region')['sales'].mean()")
    assert float(result["A"]) == 15

def test_reject_unsafe():
    df = pd.DataFrame({"x":[1]})
    try:
        safe_eval_pandas(df, "__import__('os').system('whoami')")
    except ValueError:
        return
    assert False
