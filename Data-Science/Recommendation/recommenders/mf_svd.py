import numpy as np
from scipy.sparse.linalg import svds
from scipy.sparse import csr_matrix

class SVDFactorization:
    """Matrix factorization using truncated SVD on the user-item matrix.
    Works for explicit or binarized implicit feedback.
    """
    def __init__(self, factors=50, mean_center=True):
        self.factors = int(factors)
        self.mean_center = bool(mean_center)
        self.user_means_ = None
        self.U_ = None
        self.S_ = None
        self.Vt_ = None
        self.user_map_ = None
        self.item_map_ = None
        self.inv_user_map_ = None
        self.inv_item_map_ = None

    def fit(self, R: csr_matrix, user_map, item_map):
        R = R.asfptype().tocsr()
        self.user_map_ = user_map
        self.item_map_ = item_map
        self.inv_user_map_ = {v:k for k,v in user_map.items()}
        self.inv_item_map_ = {v:k for k,v in item_map.items()}

        if self.mean_center:
            # compute mean per user (avoid NaN for empty rows)
            sums = R.sum(axis=1).A1
            counts = (R != 0).sum(axis=1).A1
            means = np.divide(sums, counts, out=np.zeros_like(sums), where=counts!=0)
            self.user_means_ = means
            # center
            R = R.tolil()
            for u in range(R.shape[0]):
                if counts[u] > 0:
                    R.data[u] = [x - means[u] for x in R.data[u]]
            R = R.tocsr()

        k = min(self.factors, min(R.shape) - 1) if min(R.shape) > 1 else 1
        U, s, Vt = svds(R, k=k)
        # sort by singular values descending
        idx = np.argsort(s)[::-1]
        self.U_ = U[:, idx]
        self.S_ = np.diag(s[idx])
        self.Vt_ = Vt[idx, :]
        return self

    def recommend(self, user_id, topk=10, exclude_seen=True, R=None):
        if user_id not in self.user_map_:
            return []
        u = self.user_map_[user_id]
        # predicted ratings: U*S*Vt
        u_vec = self.U_[u, :] @ self.S_
        scores = u_vec @ self.Vt_
        if self.mean_center and self.user_means_ is not None:
            scores = scores + self.user_means_[u]
        # filter seen items
        seen = set(R[u].indices) if (exclude_seen and R is not None) else set()
        pairs = [(i, s) for i, s in enumerate(scores) if i not in seen]
        pairs.sort(key=lambda x: x[1], reverse=True)
        return [(self.inv_item_map_[i], float(s)) for i, s in pairs[:topk]]