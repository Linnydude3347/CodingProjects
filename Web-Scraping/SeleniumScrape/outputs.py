import os, json, csv

def to_jsonl(path: str, rows):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def to_csv(path: str, rows, fieldnames=None):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    file_exists = os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        if fieldnames is None:
            # peek one row
            rows = iter(rows)
            first = next(rows, None)
            if first is None:
                return
            fieldnames = list(first.keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            if not file_exists:
                writer.writeheader()
            writer.writerow(first)
            for r in rows:
                writer.writerow(r)
        else:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            if not file_exists:
                writer.writeheader()
            for r in rows:
                writer.writerow(r)