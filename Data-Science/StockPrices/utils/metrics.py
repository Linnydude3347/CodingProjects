from __future__ import annotations
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

def rmse(y_true, y_pred):
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))

def mae(y_true, y_pred):
    return float(mean_absolute_error(y_true, y_pred))

def mape(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    denom = np.where(y_true == 0, 1e-8, np.abs(y_true))
    return float(np.mean(np.abs((y_true - y_pred) / denom)))

def r2(y_true, y_pred):
    return float(r2_score(y_true, y_pred))