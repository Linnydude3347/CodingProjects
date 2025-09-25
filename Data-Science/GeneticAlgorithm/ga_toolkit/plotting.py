from __future__ import annotations
import os
import numpy as np
import matplotlib.pyplot as plt

def ensure_dir(path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

def plot_fitness(best, mean, out_path: str, title: str = "GA Fitness"):
    ensure_dir(out_path)
    fig, ax = plt.subplots()
    ax.plot(best, label="Best")
    ax.plot(mean, label="Mean")
    ax.set_title(title)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)

def plot_tsp_route(coords, perm, out_path: str, title: str = "Best TSP Route"):
    ensure_dir(out_path)
    path = coords[perm]
    closed = np.vstack([path, path[0]])
    fig, ax = plt.subplots()
    ax.plot(closed[:,0], closed[:,1], marker="o")
    ax.set_title(title)
    ax.set_aspect("equal", adjustable="box")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)