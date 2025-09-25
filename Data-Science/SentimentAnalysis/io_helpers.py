import os, json
import pandas as pd

def read_any(path: str) -> pd.DataFrame:
    path = str(path)
    if path.lower().endswith(".jsonl"):
        # json lines with one tweet per line
        rows = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
        return pd.DataFrame(rows)
    elif path.lower().endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        if isinstance(obj, list):
            return pd.DataFrame(obj)
        return pd.json_normalize(obj)
    else:
        # assume CSV
        return pd.read_csv(path)

def write_csv(path: str, df: pd.DataFrame):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    df.to_csv(path, index=False)