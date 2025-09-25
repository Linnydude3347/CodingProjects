import argparse
import os
from scrape_selenium.scraper import scrape_quotes
from scrape_selenium.outputs import to_jsonl, to_csv

def main(argv=None):
    ap = argparse.ArgumentParser(description="Scrape with Selenium WebDriver (demo: quotes.toscrape.com).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("quotes", help="Scrape quotes.toscrape.com (demo)")
    s.add_argument("--start-url", default="https://quotes.toscrape.com/")
    s.add_argument("--max-pages", type=int, default=5)
    s.add_argument("--jsonl", help="Write output to JSONL")
    s.add_argument("--csv", help="Write output to CSV")

    args = ap.parse_args(argv)

    if args.cmd == "quotes":
        gen = scrape_quotes(args.start_url, args.max_pages)
        if args.jsonl:
            to_jsonl(args.jsonl, gen)
        elif args.csv:
            to_csv(args.csv, gen)
        else:
            # default: print first 20
            from itertools import islice
            import json
            for row in islice(gen, 20):
                print(json.dumps(row, ensure_ascii=False))

if __name__ == "__main__":
    main()