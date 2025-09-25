from __future__ import annotations
from typing import Tuple
import numpy as np

# ---------------- Continuous Benchmarks ----------------
def sphere(x: np.ndarray) -> float:
    return float(np.sum(x * x))

def rastrigin(x: np.ndarray) -> float:
    A = 10.0
    n = x.size
    return float(A * n + np.sum(x * x - A * np.cos(2 * np.pi * x)))

# ---------------- Knapsack ----------------
def knapsack_value(bits: np.ndarray, values: np.ndarray, weights: np.ndarray, capacity: float, penalty: float = 1e3) -> float:
    tot_w = float(np.sum(bits * weights))
    tot_v = float(np.sum(bits * values))
    if tot_w <= capacity:
        return tot_v  # maximize
    # penalize overweight linearly
    return tot_v - penalty * (tot_w - capacity)

def make_knapsack(n_items=50, seed: int = 42, capacity_ratio: float = 0.4) -> Tuple[np.ndarray, np.ndarray, float]:
    rng = np.random.default_rng(seed)
    values = rng.integers(10, 100, size=n_items).astype(float)
    weights = rng.integers(5, 40, size=n_items).astype(float)
    capacity = float(np.floor(np.sum(weights) * capacity_ratio))
    return values, weights, capacity

# ---------------- TSP (2D Euclidean) ----------------
def tsp_distance(perm: np.ndarray, coords: np.ndarray) -> float:
    # closed tour
    path = coords[perm]
    shifted = np.roll(path, -1, axis=0)
    d = np.sqrt(((path - shifted) ** 2).sum(axis=1)).sum()
    return float(d)

def make_cities(n=50, seed: int = 123) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.random((n, 2))  # in [0,1]^2