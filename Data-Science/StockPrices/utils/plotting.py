import os
import matplotlib.pyplot as plt

def ensure_dir(path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

def plot_forecast(dates, y_true, y_pred, out_path: str, title: str = "Forecast vs Actual"):
    ensure_dir(out_path)
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(dates, y_true, label="Actual")
    ax.plot(dates, y_pred, label="Predicted")
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Target")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)