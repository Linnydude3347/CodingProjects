import argparse, json, os, sys, joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import TimeSeriesSplit

from data_tools.loader import fetch_prices
from features.engineer import build_supervised
from models.models import make_model, NaiveLast
from utils.metrics import rmse, mae, mape, r2
from utils.plotting import plot_forecast

def cmd_fetch(args):
    df = fetch_prices(args.symbol, args.start, args.end, args.interval)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    df.to_csv(args.out)
    print(f"Wrote {args.out} with {len(df):,} rows")

def cmd_featurize(args):
    df = pd.read_csv(args.prices, parse_dates=['Date'], index_col='Date')
    sup = build_supervised(df, horizon=args.horizon, target=args.target)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    sup.to_csv(args.out)
    print(f"Wrote {args.out} with {len(sup):,} rows and {sup.shape[1]} columns")

def _train_test_split(df, test_size=0.2):
    n = len(df)
    n_test = int(n * test_size)
    train = df.iloc[:-n_test].copy()
    test = df.iloc[-n_test:].copy()
    return train, test

def _build_pipeline(model_name, model_args, feature_cols):
    scaler = StandardScaler()
    # All numeric; we scale everything except target
    pre = ColumnTransformer(
        transformers=[('num', scaler, feature_cols)],
        remainder='drop',
        n_jobs=None
    )
    model = make_model(model_name, model_args)
    pipe = Pipeline([('pre', pre), ('model', model)])
    return pipe

def cmd_evaluate(args):
    df = pd.read_csv(args.features, parse_dates=['Date'], index_col='Date')
    train, test = _train_test_split(df, test_size=args.test_size)
    X_cols = [c for c in df.columns if c != 'y']

    # Walk-forward split on train+test for robustness
    tscv = TimeSeriesSplit(n_splits=args.splits)
    X = df[X_cols].astype(float).values
    y = df['y'].astype(float).values

    rmses, maes, mapes, r2s = [], [], [], []
    for fold, (tr_idx, val_idx) in enumerate(tscv.split(X), start=1):
        Xtr, Xval = X[tr_idx], X[val_idx]
        ytr, yval = y[tr_idx], y[val_idx]
        model_args = json.loads(args.model_args) if args.model_args else None
        pipe = _build_pipeline(args.model, model_args, X_cols)
        # if NaiveLast, stash last train y
        if isinstance(pipe.named_steps['model'], NaiveLast):
            pipe.named_steps['model'].set_last(ytr[-1])
        pipe.fit(pd.DataFrame(Xtr, columns=X_cols), ytr)
        pred = pipe.predict(pd.DataFrame(Xval, columns=X_cols))
        rmses.append(rmse(yval, pred))
        maes.append(mae(yval, pred))
        mapes.append(mape(yval, pred))
        r2s.append(r2(yval, pred))
        print(f"Fold {fold}: RMSE={rmses[-1]:.6f} MAE={maes[-1]:.6f} MAPE={mapes[-1]:.4f} R2={r2s[-1]:.4f}")

    import numpy as np
    def avg(a): return float(np.mean(a)) if a else float('nan')
    print(f"Avg over {args.splits} folds -> RMSE={avg(rmses):.6f} MAE={avg(maes):.6f} MAPE={avg(mapes):.4f} R2={avg(r2s):.4f}")

def cmd_forecast(args):
    df = pd.read_csv(args.features, parse_dates=['Date'], index_col='Date')
    # simple holdout
    train, test = _train_test_split(df, test_size=args.test_size)
    X_cols = [c for c in df.columns if c != 'y']

    model_args = json.loads(args.model_args) if args.model_args else None
    pipe = _build_pipeline(args.model, model_args, X_cols)
    if isinstance(pipe.named_steps['model'], NaiveLast):
        pipe.named_steps['model'].set_last(train['y'].iloc[-1])
    pipe.fit(train.drop(columns=['y']), train['y'].values)
    pred = pipe.predict(test.drop(columns=['y']))

    # Metrics
    y_true = test['y'].values
    print(f"Holdout -> RMSE={rmse(y_true, pred):.6f} MAE={mae(y_true, pred):.6f} MAPE={mape(y_true, pred):.4f} R2={r2(y_true, pred):.4f}")

    # Plot
    if args.plot:
        title = f"Forecast ({args.model})"
        plot_forecast(test.index, y_true, pred, args.plot, title=title)
        print(f"Saved plot to {args.plot}")

    # Save model
    if args.save_model:
        os.makedirs(os.path.dirname(args.save_model) or ".", exist_ok=True)
        joblib.dump(pipe, args.save_model)
        print(f"Saved model to {args.save_model}")

    # Save predictions
    if args.save_pred:
        out = test.copy()
        out['y_pred'] = pred
        os.makedirs(os.path.dirname(args.save_pred) or ".", exist_ok=True)
        out.to_csv(args.save_pred)
        print(f"Saved predictions to {args.save_pred}")

def main(argv=None):
    ap = argparse.ArgumentParser(description="Stock Price Prediction Toolkit")
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="Download prices with yfinance")
    f.add_argument("--symbol", required=True)
    f.add_argument("--start")
    f.add_argument("--end")
    f.add_argument("--interval", default="1d")
    f.add_argument("--out", required=True)
    f.set_defaults(func=cmd_fetch)

    z = sub.add_parser("featurize", help="Build indicators & target from OHLCV CSV")
    z.add_argument("--prices", required=True, help="CSV from 'fetch' (index=Date)")
    z.add_argument("--horizon", type=int, default=1, help="Steps ahead to predict")
    z.add_argument("--target", choices=["price","return"], default="return")
    z.add_argument("--out", required=True)
    z.set_defaults(func=cmd_featurize)

    e = sub.add_parser("evaluate", help="Walk-forward evaluation")
    e.add_argument("--features", required=True)
    e.add_argument("--model", default="rf", choices=["naive","ma","linear","rf","xgb"])
    e.add_argument("--model-args", help="JSON dict of model kwargs")
    e.add_argument("--splits", type=int, default=5)
    e.add_argument("--test-size", type=float, default=0.2)
    e.set_defaults(func=cmd_evaluate)

    o = sub.add_parser("forecast", help="Fit on train, predict on holdout, and plot")
    o.add_argument("--features", required=True)
    o.add_argument("--model", default="rf", choices=["naive","ma","linear","rf","xgb"])
    o.add_argument("--model-args", help="JSON dict of model kwargs")
    o.add_argument("--test-size", type=float, default=0.2)
    o.add_argument("--plot", help="Path to save forecast plot (PNG)")
    o.add_argument("--save-model", help="Path to save fitted model (.joblib)")
    o.add_argument("--save-pred", help="Path to save predictions CSV")
    o.set_defaults(func=cmd_forecast)

    args = ap.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    main()