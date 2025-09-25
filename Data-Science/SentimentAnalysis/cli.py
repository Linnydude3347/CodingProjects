import argparse, os
import pandas as pd
from ingest import search_recent
from io_helpers import read_any, write_csv
from utils import clean_text
from sentiment import analyze_vader, analyze_hf
from visualize import plot_distribution, plot_timeseries

def cmd_fetch(args):
    rows = search_recent(
        query=args.query,
        limit=args.limit,
        max_results=args.max_results,
        start_time=args.start_time,
        end_time=args.end_time,
        bearer_token=args.bearer_token
    )
    # Write JSONL or CSV
    os.makedirs(os.path.dirname(args.jsonl or args.csv) or ".", exist_ok=True)
    if args.jsonl:
        with open(args.jsonl, "a", encoding="utf-8") as f:
            import json
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    elif args.csv:
        import csv
        first = True
        with open(args.csv, "a", encoding="utf-8", newline="") as f:
            writer = None
            for r in rows:
                if writer is None:
                    writer = csv.DictWriter(f, fieldnames=list(r.keys()))
                    if first:
                        writer.writeheader()
                        first = False
                writer.writerow(r)

def cmd_analyze(args):
    df = read_any(args.input)
    text_col = args.text_col if args.text_col in df.columns else "text"
    if text_col not in df.columns:
        raise SystemExit(f"Could not find text column '{args.text_col}' or 'text' in input.")
    # Clean text
    df["text_clean"] = df[text_col].astype(str).map(clean_text)

    # Choose model
    if args.model == "hf":
        gen = analyze_hf(df["text_clean"], model_name=args.hf_model)
    else:
        gen = analyze_vader(df["text_clean"])

    # Collect results
    sent = list(gen)
    df_out = pd.concat([df.reset_index(drop=True), pd.DataFrame(sent)], axis=1)
    # Write output
    write_csv(args.out, df_out)

def cmd_report(args):
    df = read_any(args.input)
    if "sentiment" not in df.columns:
        raise SystemExit("Input does not contain 'sentiment' column. Run analyze first.")
    plot_distribution(df, outdir=args.outdir)
    plot_timeseries(df, outdir=args.outdir)
    print(f"Saved charts to {args.outdir}")

def main(argv=None):
    ap = argparse.ArgumentParser(description="Twitter (X) Sentiment Analysis pipeline.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # fetch
    s = sub.add_parser("fetch", help="Fetch tweets via recent search (v2).")
    s.add_argument("--query", required=True, help='e.g., "(python OR pandas) lang:en -is:retweet"')
    s.add_argument("--limit", type=int, default=200)
    s.add_argument("--max-results", type=int, default=100)
    s.add_argument("--start-time")
    s.add_argument("--end-time")
    s.add_argument("--bearer-token", help="Override TWITTER_BEARER_TOKEN env var")
    out = s.add_argument_group("Output")
    out.add_argument("--jsonl", help="Write to JSONL file")
    out.add_argument("--csv", help="Write to CSV file")
    s.set_defaults(func=cmd_fetch)

    # analyze
    a = sub.add_parser("analyze", help="Score sentiment for CSV/JSONL.")
    a.add_argument("--input", required=True, help="CSV/JSONL with a text column")
    a.add_argument("--out", required=True, help="Output CSV with sentiment columns")
    a.add_argument("--text-col", default="text")
    a.add_argument("--model", choices=["vader","hf"], default="vader")
    a.add_argument("--hf-model", default="cardiffnlp/twitter-roberta-base-sentiment-latest")
    a.set_defaults(func=cmd_analyze)

    # report
    r = sub.add_parser("report", help="Create charts from analyzed CSV.")
    r.add_argument("--input", required=True)
    r.add_argument("--outdir", default="reports")
    r.set_defaults(func=cmd_report)

    args = ap.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    main()