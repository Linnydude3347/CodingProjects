import argparse
import numpy as np
from ga_toolkit.engine import GA, GAConfig
from ga_toolkit import operators as ops
from ga_toolkit import problems as P
from ga_toolkit.plotting import plot_fitness

# -------- Utilities --------
def real_bounds(dim, lo=-5.12, hi=5.12):
    lo = np.full(dim, float(lo))
    hi = np.full(dim, float(hi))
    return lo, hi

def make_real_init(dim, lo, hi, rng):
    def init():
        return rng.uniform(lo, hi, size=dim)
    return init

def make_binary_init(dim, rng):
    def init():
        return rng.integers(0, 2, size=dim).astype(int)
    return init

def make_perm_init(n, rng):
    def init():
        return rng.permutation(n).astype(int)
    return init

# -------- CLI commands --------
def cmd_optimize(args):
    rng = np.random.default_rng(args.seed)
    dim = args.dim
    lo, hi = real_bounds(dim, args.lower, args.upper)
    init_fn = make_real_init(dim, lo, hi, rng)

    # choose problem
    if args.problem == 'sphere':
        fitness = P.sphere
        minimize = True
    else:
        fitness = P.rastrigin
        minimize = True

    # operators
    if args.crossover == 'blx':
        crossover = lambda a,b,rg: ops.blx_alpha_crossover(a,b,rg, alpha=args.alpha, bounds=(lo,hi))
    elif args.crossover == 'onepoint':
        crossover = ops.one_point_crossover
    else:
        crossover = ops.uniform_crossover

    if args.mutation == 'gaussian':
        sigma = args.sigma if args.sigma is not None else 0.1 * (args.upper - args.lower)
        mutation = lambda x,rg: ops.gaussian_mutation(x, rg, sigma=sigma, bounds=(lo,hi))
    else:
        mutation = lambda x,rg: ops.gaussian_mutation(x, rg, sigma=0.1 * (args.upper - args.lower), bounds=(lo,hi))

    select = (lambda pop,fit,rg: ops.tournament_selection(pop,fit,rg,k=args.k, minimize=minimize)) if args.selection=='tournament' else (lambda pop,fit,rg: ops.roulette_selection(pop,fit,rg, minimize=minimize))

    cfg = GAConfig(pop_size=args.pop, generations=args.gens, cx_rate=args.cx_rate, mut_rate=args.mut_rate, elitism=args.elite, minimize=minimize, stall_generations=args.stall, target_fitness=args.target, seed=args.seed, n_jobs=args.jobs)
    ga = GA(fitness, init_fn, mutation, crossover, select, cfg)
    res = ga.run()

    print(f"Best fitness: {res.best_fitness:.6f}")
    if args.plot:
        plot_fitness(res.history.best_fitness, res.history.mean_fitness, args.plot, title=f"{args.problem}")

def cmd_knapsack(args):
    rng = np.random.default_rng(args.seed)
    values, weights, capacity = P.make_knapsack(n_items=args.items, seed=args.seed, capacity_ratio=args.capacity_ratio)

    def fitness(bits):
        return -1.0 * P.knapsack_value(bits, values, weights, capacity) * -1.0  # keep as numeric
    # We actually want to MAXIMIZE value; engine uses minimize flag to control; so set minimize=False and use value as fitness for maximize path.
    def fitness_max(bits):
        return P.knapsack_value(bits, values, weights, capacity)

    init = make_binary_init(len(values), rng)
    crossover = ops.one_point_crossover
    mutation = lambda x,rg: ops.bitflip_mutation(x, rg, p=args.bitflip)
    select = (lambda pop,fit,rg: ops.tournament_selection(pop,fit,rg,k=args.k, minimize=False)) if args.selection=='tournament' else (lambda pop,fit,rg: ops.roulette_selection(pop,fit,rg, minimize=False))

    cfg = GAConfig(pop_size=args.pop, generations=args.gens, cx_rate=args.cx_rate, mut_rate=args.mut_rate, elitism=args.elite, minimize=False, stall_generations=args.stall, seed=args.seed, n_jobs=args.jobs)
    ga = GA(fitness_max, init, mutation, crossover, select, cfg)
    res = ga.run()

    print(f"Best value: {res.best_fitness:.2f} (capacity={capacity:.1f})")
    if args.plot:
        plot_fitness(res.history.best_fitness, res.history.mean_fitness, args.plot, title="Knapsack")

def cmd_tsp(args):
    rng = np.random.default_rng(args.seed)
    coords = P.make_cities(n=args.cities, seed=args.seed)
    n = len(coords)
    init = make_perm_init(n, rng)
    def fitness(perm):
        return P.tsp_distance(perm, coords)  # minimize
    crossover = ops.order_crossover
    mutation = ops.swap_mutation
    select = (lambda pop,fit,rg: ops.tournament_selection(pop,fit,rg,k=args.k, minimize=True)) if args.selection=='tournament' else (lambda pop,fit,rg: ops.roulette_selection(pop,fit,rg, minimize=True))

    cfg = GAConfig(pop_size=args.pop, generations=args.gens, cx_rate=args.cx_rate, mut_rate=args.mut_rate, elitism=args.elite, minimize=True, stall_generations=args.stall, seed=args.seed, n_jobs=args.jobs)
    # Wrap mutation probability at engine-level: we'll apply or not via mut_rate, swap is single op
    def mutate_wrapper(x, rg):
        return mutation(x, rg)
    ga = GA(fitness, init, mutate_wrapper, crossover, select, cfg)
    res = ga.run()

    print(f"Best tour length: {res.best_fitness:.6f}")
    if args.plot:
        plot_fitness(res.history.best_fitness, res.history.mean_fitness, args.plot, title="TSP")
    if args.route_plot:
        from ga_toolkit.plotting import plot_tsp_route
        plot_tsp_route(coords, res.best_individual, args.route_plot, title="Best TSP Tour")

def main(argv=None):
    ap = argparse.ArgumentParser(description="Genetic Algorithms Toolkit")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # optimize (continuous)
    o = sub.add_parser("optimize", help="Optimize continuous problems (sphere, rastrigin)")
    o.add_argument("--problem", choices=["sphere","rastrigin"], default="rastrigin")
    o.add_argument("--dim", type=int, default=20)
    o.add_argument("--lower", type=float, default=-5.12)
    o.add_argument("--upper", type=float, default=5.12)
    o.add_argument("--pop", type=int, default=100)
    o.add_argument("--gens", type=int, default=200)
    o.add_argument("--cx-rate", type=float, default=0.9)
    o.add_argument("--mut-rate", type=float, default=0.2)
    o.add_argument("--elite", type=int, default=1)
    o.add_argument("--stall", type=int, default=60)
    o.add_argument("--target", type=float)
    o.add_argument("--selection", choices=["tournament","roulette"], default="tournament")
    o.add_argument("--k", type=int, default=3, help="Tournament size")
    o.add_argument("--crossover", choices=["blx","onepoint","uniform"], default="blx")
    o.add_argument("--alpha", type=float, default=0.5, help="BLX alpha")
    o.add_argument("--mutation", choices=["gaussian"], default="gaussian")
    o.add_argument("--sigma", type=float, help="Gaussian sigma (default: 0.1 * range)")
    o.add_argument("--jobs", type=int, default=1, help="Parallel workers for fitness")
    o.add_argument("--plot", help="Save fitness curve PNG")
    o.add_argument("--seed", type=int, default=42)
    o.set_defaults(func=cmd_optimize)

    # knapsack
    k = sub.add_parser("knapsack", help="0-1 Knapsack (binary encoding)")
    k.add_argument("--items", type=int, default=50)
    k.add_argument("--capacity-ratio", type=float, default=0.4)
    k.add_argument("--pop", type=int, default=120)
    k.add_argument("--gens", type=int, default=250)
    k.add_argument("--cx-rate", type=float, default=0.9)
    k.add_argument("--mut-rate", type=float, default=0.2)
    k.add_argument("--bitflip", type=float, default=0.02)
    k.add_argument("--elite", type=int, default=1)
    k.add_argument("--stall", type=int, default=80)
    k.add_argument("--selection", choices=["tournament","roulette"], default="tournament")
    k.add_argument("--k", type=int, default=3)
    k.add_argument("--jobs", type=int, default=1)
    k.add_argument("--plot", help="Save fitness curve PNG")
    k.add_argument("--seed", type=int, default=123)
    k.set_defaults(func=cmd_knapsack)

    # tsp
    t = sub.add_parser("tsp", help="Traveling Salesman Problem (permutation encoding)")
    t.add_argument("--cities", type=int, default=50)
    t.add_argument("--pop", type=int, default=160)
    t.add_argument("--gens", type=int, default=300)
    t.add_argument("--cx-rate", type=float, default=0.9)
    t.add_argument("--mut-rate", type=float, default=0.2)
    t.add_argument("--elite", type=int, default=1)
    t.add_argument("--stall", type=int, default=120)
    t.add_argument("--selection", choices=["tournament","roulette"], default="tournament")
    t.add_argument("--k", type=int, default=3)
    t.add_argument("--jobs", type=int, default=1)
    t.add_argument("--plot", help="Save fitness curve PNG")
    t.add_argument("--route-plot", help="Save best route PNG")
    t.add_argument("--seed", type=int, default=321)
    t.set_defaults(func=cmd_tsp)

    args = ap.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    main()