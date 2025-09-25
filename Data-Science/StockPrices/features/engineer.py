from __future__ import annotations
import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add common technical indicators to OHLCV DataFrame."""
    out = df.copy()
    close = out['Close']

    # Moving averages / EMA
    for w in (5, 10, 20, 50, 100, 200):
        out[f'sma_{w}'] = close.rolling(w).mean()
        out[f'ema_{w}'] = EMAIndicator(close=close, window=w).ema_indicator()

    # Momentum
    out['rsi_14'] = RSIIndicator(close, window=14).rsi()
    macd = MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
    out['macd'] = macd.macd()
    out['macd_signal'] = macd.macd_signal()
    out['macd_hist'] = macd.macd_diff()

    # Volatility (Bollinger Bands)
    bb = BollingerBands(close=close, window=20, window_dev=2)
    out['bb_high'] = bb.bollinger_hband()
    out['bb_low'] = bb.bollinger_lband()
    out['bb_width'] = out['bb_high'] - out['bb_low']

    # Returns & lags
    out['ret_1'] = close.pct_change(1)
    for lag in (1, 2, 3, 5, 10, 20):
        out[f'lag_ret_{lag}'] = out['ret_1'].shift(lag)
        out[f'lag_close_{lag}'] = close.shift(lag)

    # Rolling stats on returns
    for w in (5, 10, 20):
        out[f'roll_ret_mean_{w}'] = out['ret_1'].rolling(w).mean()
        out[f'roll_ret_std_{w}'] = out['ret_1'].rolling(w).std()

    # Volume features
    out['vol_chg'] = out['Volume'].pct_change(1).replace([np.inf, -np.inf], np.nan)

    return out

def build_supervised(df: pd.DataFrame, horizon: int = 1, target: str = 'return') -> pd.DataFrame:
    """Construct a supervised learning table.
    target: 'price' (next Close) or 'return' (next % return of Close).
    horizon: steps ahead to predict (e.g., 1 = next bar).
    """
    df = df.copy()
    df_feat = add_indicators(df)

    if target == 'price':
        y = df_feat['Close'].shift(-horizon)
        df_feat['y'] = y
    else:
        # next-period return
        future = df_feat['Close'].shift(-horizon)
        df_feat['y'] = (future / df_feat['Close'] - 1.0)

    # Drop rows with NaNs created by indicators/shift
    df_feat = df_feat.dropna()
    return df_feat