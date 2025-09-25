# Predicting Stock Prices — Data Analysis (Python)

A practical starter for end‑to‑end **stock price prediction** and evaluation. Fetch data with **yfinance**, engineer **technical indicators**, train models (from **naive baselines** to **RandomForest**), and evaluate using **time‑series walk‑forward**. Includes plotting helpers and a single CLI.

## Features
- **Fetch**: OHLCV from Yahoo via `yfinance`
- **Features**: returns, lags, rolling stats, RSI, MACD, Bollinger Bands, EMAs (via `ta`)
- **Targets**: next‑step close price or return
- **Models**: NaiveLast, MovingAverage, LinearRegression, RandomForest, (optional XGBoost)
- **Eval**: expanding-window *walk‑forward* with RMSE/MAE/MAPE/R²
- **Forecast**: out‑of‑sample prediction & plot

## Quickstart
```bash
cd stock_prediction
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
```

### 1) Fetch prices
```bash
python -m scripts.cli fetch --symbol AAPL --start 2020-01-01 --end 2025-01-01 --out data/aapl.csv
```

### 2) Build features
```bash
python -m scripts.cli featurize --prices data/aapl.csv --horizon 1 --target return --out data/aapl_features.csv
# target: 'price' (next close) or 'return' (next close % return)
```

### 3) Train & evaluate (walk‑forward)
```bash
python -m scripts.cli evaluate --features data/aapl_features.csv --model rf --topk 20 --splits 5
```

### 4) Forecast last segment & plot
```bash
python -m scripts.cli forecast --features data/aapl_features.csv --model rf --plot outputs/aapl_forecast.png --save-model models/aapl_rf.joblib
```

## Notes
- **Leakage**: All features use only *past* info; standardization is fit on train each fold.
- **Stationarity**: Predicting returns tends to be more stable than raw prices.
- **Hyper‑params**: Tune `--model-args` JSON for models (see help).
- **Intervals**: Use `--interval` when fetching (e.g., `1d`, `1h`) if desired.

## Help
```bash
python -m scripts.cli -h
python -m scripts.cli featurize -h
python -m scripts.cli evaluate -h
python -m scripts.cli forecast -h
```