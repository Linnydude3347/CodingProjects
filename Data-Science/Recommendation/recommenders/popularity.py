import pandas as pd

class PopularityRecommender:
    """Popularity baseline.
    mode='count' uses interaction count; mode='mean' uses mean rating.
    """
    def __init__(self, mode: str = "count"):
        assert mode in {"count", "mean"}
        self.mode = mode
        self.item_scores_ = None

    def fit(self, interactions: pd.DataFrame):
        if self.mode == "count":
            s = interactions.groupby("item_id").size().rename("score")
        else:
            if "rating" not in interactions.columns:
                raise ValueError("mode='mean' requires a 'rating' column")
            s = interactions.groupby("item_id")["rating"].mean().rename("score")
        self.item_scores = s.sort_values(ascending=False)
        return self

    def recommend(self, user_id, seen_items, topk=10):
        seen = set(seen_items or [])
        recs = [i for i in self.item_scores.index if i not in seen][:topk]
        return [(iid, float(self.item_scores.loc[iid])) for iid in recs]