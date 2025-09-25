from __future__ import annotations
import pandas as pd
from scipy.sparse import csr_matrix

def load_ratings_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # standardize column names
    cols = {c.lower().strip(): c for c in df.columns}
    def pick(*names):
        for n in names:
            if n in cols: return cols[n]
        return None
    uid = pick('user_id','user','userid','u')
    iid = pick('item_id','item','movieid','i','productid')
    rating = pick('rating','score','value')
    ts = pick('timestamp','time','ts')
    out = pd.DataFrame({
        'user_id': df[uid].astype(str),
        'item_id': df[iid].astype(str),
    })
    if rating:
        out['rating'] = pd.to_numeric(df[rating], errors='coerce')
    if ts:
        out['timestamp'] = df[ts]
    return out

def build_interaction_matrix(df: pd.DataFrame, implicit: bool = False, threshold: float = 0.0):
    """Return (R, user_map, item_map)
    - R: csr_matrix shape (n_users, n_items)
    - user_map: id->row, item_map: id->col
    If implicit=True, convert rating to 1.0 if > threshold else 0.
    """
    users = df['user_id'].astype(str).unique()
    items = df['item_id'].astype(str).unique()
    u_index = {u:i for i,u in enumerate(users)}
    i_index = {m:i for i,m in enumerate(items)}
    rows = df['user_id'].astype(str).map(u_index)
    cols = df['item_id'].astype(str).map(i_index)
    if implicit or 'rating' not in df.columns:
        vals = (df.get('rating', 1.0) > threshold).astype(float)
        vals = vals.where(vals > 0, 0.0).astype(float)
    else:
        vals = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0).astype(float)

    R = csr_matrix((vals, (rows, cols)), shape=(len(users), len(items)))
    return R, u_index, i_index

def leave_one_out_split(df: pd.DataFrame, min_user_interactions: int = 2):
    """For each user with >= min interactions, keep the most recent (or last) as test, rest train."""
    if 'timestamp' in df.columns:
        df_sorted = df.sort_values(['user_id','timestamp'])
    else:
        df_sorted = df.sort_values(['user_id'])
    test = df_sorted.groupby('user_id').tail(1)
    train = pd.concat([df_sorted, test]).drop_duplicates(keep=False)
    # Filter out users with not enough interactions
    counts = train.groupby('user_id').size()
    keep_users = counts[counts >= (min_user_interactions - 1)].index
    train = train[train['user_id'].isin(keep_users)]
    test = test[test['user_id'].isin(keep_users)]
    return train, test

def get_user_seen_items(df: pd.DataFrame):
    return df.groupby('user_id')['item_id'].apply(set).to_dict()