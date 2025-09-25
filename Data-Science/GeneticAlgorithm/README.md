# Genetic Algorithms — Data Analysis Toolkit (Python)

A clean, extensible **Genetic Algorithms** starter with multiple encodings (real, binary, integer, permutation), pluggable operators, classic benchmarks, and a simple CLI.

## Features
- **Encodings**: real‑valued, binary, integer, and permutation (for TSP)
- **Selection**: tournament, roulette (rank‑safe)
- **Crossover**: one‑point, uniform (binary/int), BLX‑alpha (real), order crossover OX (permutation)
- **Mutation**: gaussian (real), bit‑flip (binary), random‑reset (int), swap (perm)
- **Elitism**, **stopping criteria** (max gens, stall gens, or target)
- **Problems**: Sphere / Rastrigin (continuous), **Knapsack 0‑1**, **TSP** (2D Euclidean)
- **Plots**: fitness curves; TSP route plot
- **Reproducible**: global `--seed`

## Quickstart
```bash
cd genetic_algorithms
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
```

### Optimize Rastrigin (real encoding)
```bash
python -m scripts.cli optimize       --problem rastrigin --dim 20       --pop 120 --gens 200 --crossover blx --mutation gaussian       --cx-rate 0.9 --mut-rate 0.2 --seed 42       --plot outputs/rastrigin_curve.png
```

### Knapsack 0‑1 (binary)
```bash
python -m scripts.cli knapsack       --items 60 --capacity-ratio 0.35       --pop 150 --gens 250 --selection tournament --k 4       --plot outputs/knapsack_curve.png
```

### Traveling Salesman (permutation)
```bash
python -m scripts.cli tsp       --cities 60 --pop 180 --gens 400       --cx-rate 0.9 --mut-rate 0.2       --plot outputs/tsp_curve.png --route-plot outputs/tsp_route.png
```

## Notes
- Fitness is **minimized** by default for continuous (Sphere/Rastrigin), **maximized** for Knapsack. TSP minimizes tour length.
- BLX‑alpha default α=0.5; gaussian mutation scales to per‑gene range.
- Roulette selection uses rank scaling for numerical stability.