import argparse, os, random, csv

def main():
    ap = argparse.ArgumentParser(description='Generate a tiny synthetic ratings CSV for testing.')
    ap.add_argument('--users', type=int, default=20)
    ap.add_argument('--items', type=int, default=30)
    ap.add_argument('--density', type=float, default=0.15, help='Fraction of possible interactions observed')
    ap.add_argument('--out', default='data/synth_ratings.csv')
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    users = [f'u_{i+1}' for i in range(args.users)]
    items = [f'i_{j+1}' for j in range(args.items)]
    total = args.users * args.items
    obs = int(total * args.density)

    seen = set()
    rows = []
    while len(rows) < obs:
        u = random.choice(users)
        i = random.choice(items)
        if (u,i) in seen: continue
        seen.add((u,i))
        rating = random.choice([1,2,3,4,5])
        rows.append((u,i,rating))

    with open(args.out, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['user_id','item_id','rating'])
        w.writerows(rows)
    print('Wrote', args.out)

if __name__ == '__main__':
    main()