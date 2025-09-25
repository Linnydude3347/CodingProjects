from __future__ import annotations
import numpy as np
from typing import Dict, Any
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

try:
    import xgboost as xgb  # optional
    _HAVE_XGB = True
except Exception:
    _HAVE_XGB = False

# --- Baselines ---
class NaiveLast:
    def fit(self, X, y):
        return self
    def predict(self, X):
        # fallback to last known value: expects last 'Close' or last y
        # Caller will pass a pipeline where we stash last y on fit
        return np.repeat(getattr(self, "_last_y", 0.0), X.shape[0])
    def set_last(self, y_last):
        self._last_y = float(y_last)
        return self

class MovingAverageBaseline:
    def __init__(self, window=5):
        self.window = int(window)
        self.history_ = None
    def fit(self, X, y):
        self.history_ = np.array(y)[-self.window:]
        return self
    def predict(self, X):
        if self.history_ is None or len(self.history_) == 0:
            return np.zeros(X.shape[0])
        avg = float(np.mean(self.history_))
        return np.repeat(avg, X.shape[0])

# --- ML Models ---
def make_model(name: str, model_args: Dict[str, Any] | None = None):
    name = name.lower()
    model_args = model_args or {}
    if name in {"naive", "naive_last"}:
        return NaiveLast()
    if name in {"ma", "moving_average"}:
        return MovingAverageBaseline(window=model_args.get("window", 5))
    if name in {"linreg", "linear", "ols"}:
        return LinearRegression(**model_args)
    if name in {"rf", "random_forest"}:
        default = dict(n_estimators=300, max_depth=None, random_state=42, n_jobs=-1)
        default.update(model_args)
        return RandomForestRegressor(**default)
    if name in {"xgb", "xgboost"}:
        if not _HAVE_XGB:
            raise RuntimeError("xgboost not installed. Uncomment it in requirements.txt and install.")
        default = dict(n_estimators=400, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1)
        default.update(model_args)
        return xgb.XGBRegressor(**default)
    raise ValueError(f"Unknown model: {name}")