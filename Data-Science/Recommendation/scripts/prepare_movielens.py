import argparse, os, zipfile, io, csv, urllib.request

URLS = {
    'ml-100k': 'https://files.grouplens.org/datasets/movielens/ml-100k.zip',
    'ml-latest-small': 'https://files.grouplens.org/datasets/movielens/ml-latest-small.zip',
}

def download_and_extract(url, dest):
    os.makedirs(dest, exist_ok=True)
    print(f'Downloading {url} ...')
    with urllib.request.urlopen(url) as resp:
        data = resp.read()
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        zf.extractall(dest)
    print('Done.')

def prepare_ml_100k(dest):
    base = os.path.join(dest, 'ml-100k')
    inpath = os.path.join(base, 'u.data')
    outpath = os.path.join(base, 'ratings.csv')
    with open(inpath, 'r', encoding='latin-1') as f, open(outpath, 'w', encoding='utf-8', newline='') as out:
        w = csv.writer(out)
        w.writerow(['user_id','item_id','rating','timestamp'])
        for line in f:
            u, i, r, t = line.strip().split('\t')
            w.writerow([u, i, r, t])
    # items
    item_in = os.path.join(base, 'u.item')
    items_out = os.path.join(base, 'items.csv')
    with open(item_in, 'r', encoding='latin-1') as f, open(items_out, 'w', encoding='utf-8', newline='') as out:
        w = csv.writer(out)
        w.writerow(['item_id','title'])
        for line in f:
            parts = line.strip().split('|')
            w.writerow([parts[0], parts[1]])

def prepare_ml_latest_small(dest):
    # already has ratings.csv & movies.csv
    pass

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dest', default='data/raw')
    ap.add_argument('--variant', choices=['ml-100k','ml-latest-small'], default='ml-100k')
    args = ap.parse_args()
    url = URLS[args.variant]
    download_and_extract(url, args.dest)
    if args.variant == 'ml-100k':
        prepare_ml_100k(args.dest)
    print('Prepared at', os.path.join(args.dest, args.variant))

if __name__ == '__main__':
    main()