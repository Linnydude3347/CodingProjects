import argparse, collections, json, re

WORD_RE = re.compile(r"[A-Za-z][A-Za-z']+")
URL_RE = re.compile(r"https?://\S+")
MENTION_RE = re.compile(r"@\w+")

def iter_texts(paths):
    for p in paths:
        with open(p, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    yield obj.get('text') or ''
                except Exception:
                    continue

def tokenize(text: str):
    text = URL_RE.sub('', text)
    text = MENTION_RE.sub('', text)
    return [w.lower() for w in WORD_RE.findall(text)]

def main(argv=None):
    ap = argparse.ArgumentParser(description='Quick n-gram stats from JSONL tweets.')
    ap.add_argument('jsonl', nargs='+', help='One or more .jsonl files')
    ap.add_argument('--top', type=int, default=25, help='Top N words to show')
    args = ap.parse_args(argv)

    counter = collections.Counter()
    for text in iter_texts(args.jsonl):
        counter.update(tokenize(text))

    for word, count in counter.most_common(args.top):
        print(f"{word}\t{count}")

if __name__ == '__main__':
    main()