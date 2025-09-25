import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

class _BaseKNN:
    def __init__(self, kind='item', k=50, shrink=0.0, min_common=1):
        assert kind in {'item','user'}
        self.kind = kind
        self.k = int(k)
        self.shrink = float(shrink)
        self.min_common = int(min_common)
        self.sim_ = None  # similarity matrix
        self.R_ = None    # interaction matrix (csr)
        self.user_map_ = None
        self.item_map_ = None
        self.inv_user_map_ = None
        self.inv_item_map_ = None

    def fit(self, R: csr_matrix, user_map, item_map):
        """R: csr of shape (n_users, n_items) with implicit (0/1) or explicit ratings.
        user_map/item_map: dicts id->index
        """
        self.R_ = R.tocsr()
        self.user_map_ = user_map
        self.item_map_ = item_map
        self.inv_user_map_ = {v:k for k,v in user_map.items()}
        self.inv_item_map_ = {v:k for k,v in item_map.items()}

        if self.kind == 'item':
            X = self.R_.T  # items x users
        else:
            X = self.R_    # users x items

        # cosine similarity; set diagonal to 0 later
        sim = cosine_similarity(X, dense_output=False)
        sim.setdiag(0.0)
        sim.eliminate_zeros()

        # k-nearest neighbors: keep top-k per row
        if self.k and self.k < sim.shape[1]:
            sim = self._topk(sim, self.k)

        if self.shrink > 0:
            # shrinkage: s' = s * n_common / (n_common + shrink)
            # approximate n_common by binary dot-products
            # (X>0) dot (X>0)^T
            B = (X > 0).astype(np.float32)
            nn = B @ B.T
            nn.setdiag(0)
            nn = nn.maximum(nn.T)  # symm-ish
            nn = nn.tocsr()
            nn.data = nn.data / (nn.data + self.shrink)
            sim = sim.multiply(nn)

        self.sim_ = sim.tocsr()
        return self

    def _topk(self, M, k):
        # keep top-k entries per row of sparse matrix
        M = M.tolil()
        for i, (data, rows) in enumerate(zip(M.data, M.rows)):
            if len(data) > k:
                idx = np.argpartition(np.array(data), -k)[-k:]
                M.data[i] = list(np.array(data)[idx])
                M.rows[i] = list(np.array(rows)[idx])
        return M.tocsr()

    def recommend(self, user_id, topk=10, exclude_seen=True):
        if user_id not in self.user_map_:
            return []  # cold user
        uidx = self.user_map_[user_id]
        if self.kind == 'item':
            # score = R_u * S_item
            user_profile = self.R_[uidx]  # 1 x n_items
            scores = user_profile @ self.sim_  # 1 x n_items
            scores = scores.toarray().ravel()
            seen = set(self.R_[uidx].indices) if exclude_seen else set()
            pairs = [(i, s) for i, s in enumerate(scores) if i not in seen and s > 0]
            pairs.sort(key=lambda x: x[1], reverse=True)
            items = [(self.inv_item_map_[i], float(s)) for i, s in pairs[:topk]]
            return items
        else:
            # user-based: scores = S_user[u] * R
            scores = self.sim_.getrow(uidx) @ self.R_
            scores = scores.toarray().ravel()
            seen = set(self.R_[uidx].indices) if exclude_seen else set()
            pairs = [(i, s) for i, s in enumerate(scores) if i not in seen and s > 0]
            pairs.sort(key=lambda x: x[1], reverse=True)
            items = [(self.inv_item_map_[i], float(s)) for i, s in pairs[:topk]]
            return items

class ItemKNN(_BaseKNN):
    def __init__(self, **kw):
        super().__init__(kind='item', **kw)

class UserKNN(_BaseKNN):
    def __init__(self, **kw):
        super().__init__(kind='user', **kw)