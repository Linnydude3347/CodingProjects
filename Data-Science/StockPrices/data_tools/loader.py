from __future__ import annotations
import pandas as pd
import yfinance as yf

def fetch_prices(symbol: str, start: str = None, end: str = None, interval: str = "1d") -> pd.DataFrame:
    """Download OHLCV with yfinance. Returns a DataFrame indexed by Datetime, columns:
    ['Open','High','Low','Close','Adj Close','Volume'].
    """
    df = yf.download(symbol, start=start, end=end, interval=interval, auto_adjust=False, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        # yfinance can return multi-index with single symbol
        df.columns = df.columns.get_level_values(0)
    df = df.rename_axis('Date').sort_index()
    return df