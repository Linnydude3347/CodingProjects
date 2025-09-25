from __future__ import annotations
from typing import List, Tuple, Any
import numpy as np

# ---------------- Selection ----------------
def tournament_selection(pop: List[Any], fitness: np.ndarray, rng: np.random.Generator, k: int = 3, minimize: bool = True) -> Any:
    idx = rng.choice(len(pop), size=k, replace=False)
    if minimize:
        best = idx[np.argmin(fitness[idx])]
    else:
        best = idx[np.argmax(fitness[idx])]
    return pop[int(best)]

def roulette_selection(pop: List[Any], fitness: np.ndarray, rng: np.random.Generator, minimize: bool = True) -> Any:
    # rank-based scaling for stability
    ranks = np.argsort(fitness) if minimize else np.argsort(-fitness)
    probs = np.empty_like(fitness, dtype=float)
    probs[ranks] = np.linspace(1.0, 2.0, num=len(fitness))  # higher rank -> higher prob
    probs = probs / probs.sum()
    idx = rng.choice(len(pop), p=probs)
    return pop[int(idx)]

# ---------------- Crossover ----------------
def one_point_crossover(a: np.ndarray, b: np.ndarray, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    n = len(a)
    if n < 2:
        return a.copy(), b.copy()
    cx = rng.integers(1, n)
    c1 = np.concatenate([a[:cx], b[cx:]])
    c2 = np.concatenate([b[:cx], a[cx:]])
    return c1, c2

def uniform_crossover(a: np.ndarray, b: np.ndarray, rng: np.random.Generator, p: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
    mask = rng.random(len(a)) < p
    c1 = a.copy()
    c2 = b.copy()
    c1[mask] = b[mask]
    c2[mask] = a[mask]
    return c1, c2

def blx_alpha_crossover(a: np.ndarray, b: np.ndarray, rng: np.random.Generator, alpha: float = 0.5, bounds: Tuple[np.ndarray, np.ndarray] | None = None) -> Tuple[np.ndarray, np.ndarray]:
    low = np.minimum(a, b)
    high = np.maximum(a, b)
    range_ = high - low
    minv = low - alpha * range_
    maxv = high + alpha * range_
    c1 = rng.uniform(minv, maxv)
    c2 = rng.uniform(minv, maxv)
    if bounds is not None:
        lo, hi = bounds
        c1 = np.clip(c1, lo, hi)
        c2 = np.clip(c2, lo, hi)
    return c1, c2

# Permutation crossover: Order Crossover (OX)
def order_crossover(a: np.ndarray, b: np.ndarray, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    n = len(a)
    i, j = sorted(rng.choice(n, size=2, replace=False))
    def ox(p1, p2):
        child = -np.ones(n, dtype=int)
        child[i:j] = p1[i:j]
        fill = [x for x in p2 if x not in child]
        pos = 0
        for k in range(n):
            if child[k] == -1:
                child[k] = fill[pos]
                pos += 1
        return child
    return ox(a, b), ox(b, a)

# ---------------- Mutation ----------------
def gaussian_mutation(x: np.ndarray, rng: np.random.Generator, sigma: float = 0.1, bounds: Tuple[np.ndarray, np.ndarray] | None = None) -> np.ndarray:
    y = x + rng.normal(0.0, sigma, size=x.shape)
    if bounds is not None:
        lo, hi = bounds
        y = np.clip(y, lo, hi)
    return y

def bitflip_mutation(x: np.ndarray, rng: np.random.Generator, p: float = 0.01) -> np.ndarray:
    mask = rng.random(len(x)) < p
    y = x.copy()
    y[mask] = 1 - y[mask]
    return y

def random_reset_mutation(x: np.ndarray, rng: np.random.Generator, lo: np.ndarray, hi: np.ndarray, p: float = 0.05) -> np.ndarray:
    y = x.copy()
    mask = rng.random(len(x)) < p
    y[mask] = rng.integers(lo[mask], hi[mask] + 1)
    return y

# Permutation swap mutation
def swap_mutation(perm: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    a, b = rng.choice(len(perm), size=2, replace=False)
    y = perm.copy()
    y[a], y[b] = y[b], y[a]
    return y