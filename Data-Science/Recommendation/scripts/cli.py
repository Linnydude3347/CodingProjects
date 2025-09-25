import argparse
import pandas as pd
from utils.data import load_ratings_csv, build_interaction_matrix, leave_one_out_split, get_user_seen_items
from utils.metrics import precision_at_k, recall_at_k, average_precision, ndcg
from recommenders.popularity import PopularityRecommender
from recommenders.knn import ItemKNN, UserKNN
from recommenders.mf_svd import SVDFactorization
from recommenders.content import ContentBased

def build_algo(name, args):
    name = name.lower()
    if name == 'pop':
        return PopularityRecommender(mode=args.pop_mode)
    if name == 'userknn':
        return UserKNN(k=args.k, shrink=args.shrink)
    if name == 'itemknn':
        return ItemKNN(k=args.k, shrink=args.shrink)
    if name == 'svd':
        return SVDFactorization(factors=args.factors, mean_center=not args.no_center)
    if name == 'content':
        return ContentBased(text_columns=tuple(args.text_cols.split(',')))
    raise SystemExit(f"Unknown algo: {name}")

def cmd_eval(args):
    df = load_ratings_csv(args.ratings)
    if args.implicit or 'rating' not in df.columns:
        df['rating'] = 1.0
    train, test = leave_one_out_split(df, min_user_interactions=args.min_user_interactions)
    R, u_map, i_map = build_interaction_matrix(train, implicit=args.implicit, threshold=args.threshold)
    user_seen_train = get_user_seen_items(train)

    algo = build_algo(args.algo, args)
    if args.algo == 'content':
        if not args.items:
            raise SystemExit('Content-based requires --items metadata CSV')
        items_df = pd.read_csv(args.items)
        algo.fit(items_df[['item_id'] + args.text_cols.split(',')])
    elif args.algo == 'pop':
        algo.fit(train)
    else:
        algo.fit(R, u_map, i_map)

    # Evaluate
    users = sorted(set(train['user_id']).intersection(set(test['user_id'])))
    k = args.topk
    precs, recs, maps, ndcgs = [], [], [], []
    for u in users:
        relevant = set(test[test['user_id'] == u]['item_id'].values)
        if args.algo == 'svd':
            recs_u = algo.recommend(u, topk=k, exclude_seen=True, R=R)
        elif args.algo == 'content':
            recs_u = algo.recommend(u, user_seen_train.get(u, []), topk=k)
        elif args.algo == 'pop':
            recs_u = algo.recommend(u, user_seen_train.get(u, []), topk=k)
        else:
            recs_u = algo.recommend(u, topk=k, exclude_seen=True)
        precs.append(precision_at_k(recs_u, relevant, k))
        recs.append(recall_at_k(recs_u, relevant, k))
        maps.append(average_precision(recs_u, relevant, k))
        ndcgs.append(ndcg(recs_u, relevant, k))

    import numpy as np
    def s(a): return float(np.mean(a)) if a else 0.0
    print(f"Users evaluated: {len(users)}")
    print(f"Precision@{k}: {s(precs):.4f}")
    print(f"Recall@{k}:    {s(recs):.4f}")
    print(f"MAP@{k}:       {s(maps):.4f}")
    print(f"NDCG@{k}:      {s(ndcgs):.4f}")

def cmd_recommend(args):
    df = load_ratings_csv(args.ratings)
    if args.implicit or 'rating' not in df.columns:
        df['rating'] = 1.0
    R, u_map, i_map = build_interaction_matrix(df, implicit=args.implicit, threshold=args.threshold)
    algo = build_algo(args.algo, args)

    if args.algo == 'content':
        if not args.items:
            raise SystemExit('Content-based requires --items metadata CSV')
        items_df = pd.read_csv(args.items)
        algo.fit(items_df[['item_id'] + args.text_cols.split(',')])
        # Build user history
        user_hist = set(df[df['user_id'] == args.user]['item_id'].astype(str).tolist())
        recs = algo.recommend(args.user, user_hist, topk=args.topk)
    elif args.algo == 'pop':
        algo.fit(df)
        user_hist = set(df[df['user_id'] == args.user]['item_id'].astype(str).tolist())
        recs = algo.recommend(args.user, user_hist, topk=args.topk)
    elif args.algo == 'svd':
        algo.fit(R, u_map, i_map)
        recs = algo.recommend(args.user, topk=args.topk, exclude_seen=True, R=R)
    else:
        algo.fit(R, u_map, i_map)
        recs = algo.recommend(args.user, topk=args.topk, exclude_seen=True)

    for iid, score in recs:
        print(f"{iid}, {score:.6f}")

def main(argv=None):
    ap = argparse.ArgumentParser(description='Recommendation Systems Toolkit')
    sub = ap.add_subparsers(dest='cmd', required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--algo', required=True, choices=['pop','userknn','itemknn','svd','content'])
    common.add_argument('--implicit', action='store_true', help='Treat data as implicit (binarize)')
    common.add_argument('--threshold', type=float, default=0.0, help='Rating > threshold => 1 (implicit)')
    common.add_argument('--topk', type=int, default=10)
    common.add_argument('--k', type=int, default=50, help='Neighbors for KNN')
    common.add_argument('--shrink', type=float, default=0.0, help='Shrinkage for KNN similarity')
    common.add_argument('--factors', type=int, default=50, help='Latent factors for SVD')
    common.add_argument('--no-center', action='store_true', help='Disable mean-centering in SVD')
    common.add_argument('--pop-mode', default='count', choices=['count','mean'])
    common.add_argument('--items', help='Item metadata CSV (for content-based)')
    common.add_argument('--text-cols', default='title,genres', help='Comma-separated text columns')

    e = sub.add_parser('eval', parents=[common], help='Evaluate with leave-one-out')
    e.add_argument('--ratings', required=True)
    e.add_argument('--min-user-interactions', type=int, default=3)
    e.set_defaults(func=cmd_eval)

    r = sub.add_parser('recommend', parents=[common], help='Recommend for a single user')
    r.add_argument('--ratings', required=True)
    r.add_argument('--user', required=True, help='User id for recommendations')
    r.set_defaults(func=cmd_recommend)

    args = ap.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    main()