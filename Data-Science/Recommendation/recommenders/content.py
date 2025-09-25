import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentBased:
    def __init__(self, text_columns=('title','genres'), max_features=5000, ngram_range=(1,2)):
        self.text_columns = text_columns
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vectorizer_ = None
        self.item_tfidf_ = None
        self.item_index_ = None  # item_id -> row index

    def fit(self, items_df: pd.DataFrame):
        texts = []
        ids = []
        for _, row in items_df.iterrows():
            parts = []
            for col in self.text_columns:
                if col in items_df.columns and pd.notna(row.get(col, "")):
                    parts.append(str(row[col]))
            texts.append(" ".join(parts))
            ids.append(row["item_id"])
        self.vectorizer_ = TfidfVectorizer(max_features=self.max_features, ngram_range=self.ngram_range)
        self.item_tfidf_ = self.vectorizer_.fit_transform(texts)
        self.item_index_ = {iid: i for i, iid in enumerate(ids)}
        return self

    def recommend(self, user_id, user_seen_items, topk=10):
        if not user_seen_items:
            # cold user: return most "central" items by tfidf norm
            norms = self.item_tfidf_.power(2).sum(axis=1).A1
            idx = np.argsort(-norms)[:topk]
            inv = {v:k for k,v in self.item_index_.items()}
            return [(inv[i], float(norms[i])) for i in idx]
        indices = [self.item_index_[iid] for iid in user_seen_items if iid in self.item_index_]
        if not indices:
            return []
        profile = self.item_tfidf_[indices].mean(axis=0)  # average liked items
        sims = cosine_similarity(profile, self.item_tfidf_).ravel()
        seen = set(indices)
        pairs = [(i, s) for i, s in enumerate(sims) if i not in seen]
        pairs.sort(key=lambda x: x[1], reverse=True)
        inv = {v:k for k,v in self.item_index_.items()}
        return [(inv[i], float(s)) for i, s in pairs[:topk]]