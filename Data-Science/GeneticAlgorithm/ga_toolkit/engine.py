from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Tuple, Any, Optional
import numpy as np
from joblib import Parallel, delayed

FitnessFn = Callable[[Any], float]
InitFn = Callable[[], Any]
MutateFn = Callable[[Any, np.random.Generator], Any]
CrossoverFn = Callable[[Any, Any, np.random.Generator], Tuple[Any, Any]]
SelectFn = Callable[[List[Any], np.ndarray, np.random.Generator], Any]

@dataclass
class GAConfig:
    pop_size: int = 100
    generations: int = 200
    cx_rate: float = 0.9
    mut_rate: float = 0.1
    elitism: int = 1
    minimize: bool = True
    stall_generations: int = 50
    target_fitness: Optional[float] = None
    seed: Optional[int] = None
    n_jobs: int = 1  # parallel fitness eval

@dataclass
class GAHistory:
    best_fitness: List[float] = field(default_factory=list)
    mean_fitness: List[float] = field(default_factory=list)
    std_fitness: List[float] = field(default_factory=list)

@dataclass
class GAResult:
    best_individual: Any
    best_fitness: float
    history: GAHistory
    generations: int

class GA:
    def __init__(
        self,
        fitness_fn: FitnessFn,
        init_fn: InitFn,
        mutate_fn: MutateFn,
        crossover_fn: CrossoverFn,
        select_fn: SelectFn,
        config: GAConfig,
    ):
        self.fitness_fn = fitness_fn
        self.init_fn = init_fn
        self.mutate_fn = mutate_fn
        self.crossover_fn = crossover_fn
        self.select_fn = select_fn
        self.cfg = config
        self.rng = np.random.default_rng(self.cfg.seed)

    def _eval_pop(self, pop: List[Any]) -> np.ndarray:
        if self.cfg.n_jobs and self.cfg.n_jobs > 1:
            fits = Parallel(n_jobs=self.cfg.n_jobs)(delayed(self.fitness_fn)(ind) for ind in pop)
            return np.asarray(fits, dtype=float)
        else:
            return np.asarray([self.fitness_fn(ind) for ind in pop], dtype=float)

    def run(self) -> GAResult:
        # init
        pop = [self.init_fn() for _ in range(self.cfg.pop_size)]
        fits = self._eval_pop(pop)
        history = GAHistory()

        best_idx = int(np.argmin(fits) if self.cfg.minimize else np.argmax(fits))
        best = pop[best_idx]
        best_fit = float(fits[best_idx])
        stall = 0

        for gen in range(1, self.cfg.generations + 1):
            history.best_fitness.append(float(np.min(fits) if self.cfg.minimize else np.max(fits)))
            history.mean_fitness.append(float(np.mean(fits)))
            history.std_fitness.append(float(np.std(fits)))

            # Elitism
            if self.cfg.elitism > 0:
                elite_idx = np.argsort(fits) if self.cfg.minimize else np.argsort(-fits)
                elites = [pop[i] for i in elite_idx[: self.cfg.elitism]]
                elite_fits = fits[elite_idx[: self.cfg.elitism]]
            else:
                elites = []
                elite_fits = np.empty((0,), dtype=float)

            # New generation
            new_pop: List[Any] = list(elites)
            while len(new_pop) < self.cfg.pop_size:
                p1 = self.select_fn(pop, fits, self.rng)
                p2 = self.select_fn(pop, fits, self.rng)
                c1, c2 = p1, p2
                if self.rng.random() < self.cfg.cx_rate:
                    c1, c2 = self.crossover_fn(p1, p2, self.rng)
                # Mutate
                if self.rng.random() < self.cfg.mut_rate:
                    c1 = self.mutate_fn(c1, self.rng)
                if len(new_pop) + 1 < self.cfg.pop_size:
                    if self.rng.random() < self.cfg.mut_rate:
                        c2 = self.mutate_fn(c2, self.rng)
                    new_pop.extend([c1, c2])
                else:
                    new_pop.append(c1)

            pop = new_pop[: self.cfg.pop_size]
            fits = self._eval_pop(pop)

            # Track best
            curr_best_idx = int(np.argmin(fits) if self.cfg.minimize else np.argmax(fits))
            curr_best = pop[curr_best_idx]
            curr_fit = float(fits[curr_best_idx])
            improved = (curr_fit < best_fit) if self.cfg.minimize else (curr_fit > best_fit)
            if improved:
                best, best_fit = curr_best, curr_fit
                stall = 0
            else:
                stall += 1

            # Stopping conditions
            if self.cfg.target_fitness is not None:
                if (best_fit <= self.cfg.target_fitness and self.cfg.minimize) or (best_fit >= self.cfg.target_fitness and not self.cfg.minimize):
                    break
            if self.cfg.stall_generations and stall >= self.cfg.stall_generations:
                break

        return GAResult(best, best_fit, history, gen)