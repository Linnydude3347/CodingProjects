import os
import pandas as pd
import matplotlib.pyplot as plt

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def plot_distribution(df: pd.DataFrame, outdir: str = "reports"):
    ensure_dir(outdir)
    ax = df["sentiment"].value_counts().reindex(["negative","neutral","positive"]).plot(kind="bar")
    ax.set_title("Sentiment Distribution")
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Count")
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "sentiment_distribution.png"))
    plt.close(fig)

def plot_timeseries(df: pd.DataFrame, outdir: str = "reports"):
    ensure_dir(outdir)
    if "created_at" not in df.columns:
        return
    tmp = df.dropna(subset=["created_at"]).copy()
    if tmp.empty:
        return
    tmp["created_at"] = pd.to_datetime(tmp["created_at"])
    ts = tmp.set_index("created_at").resample("H")["sentiment_score"].mean()
    ax = ts.plot()
    ax.set_title("Average Sentiment Score Over Time (hourly)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Avg compound score")
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "sentiment_timeseries.png"))
    plt.close(fig)