import argparse, os, sys
from twitter_mining.api import TwitterClient
from twitter_mining.storage import to_jsonl, to_csv, to_sqlite

def main(argv=None):
    ap = argparse.ArgumentParser(description='Mine Twitter (X) data via the official v2 API.')
    sub = ap.add_subparsers(dest='cmd', required=True)

    s = sub.add_parser('search', help='Recent search (last ~7 days).')
    s.add_argument('--query', required=True, help='v2 query string, e.g., "(python OR pandas) lang:en -is:retweet"')
    s.add_argument('--limit', type=int, default=1000, help='Total tweets to fetch')
    s.add_argument('--max-results', type=int, default=100, help='Per-request (10..100)')
    s.add_argument('--start-time', help='ISO 8601 start_time (e.g., 2025-09-01T00:00:00Z)')
    s.add_argument('--end-time', help='ISO 8601 end_time (e.g., 2025-09-02T00:00:00Z)')

    out = s.add_argument_group('Output')
    out.add_argument('--jsonl', help='Write to JSONL file')
    out.add_argument('--csv', help='Write to CSV file')
    out.add_argument('--sqlite', help='Write into SQLite file')
    out.add_argument('--table', default='tweets', help='SQLite table name')

    s.add_argument('--bearer-token', help='Override TWITTER_BEARER_TOKEN env var')
    args = ap.parse_args(argv)

    if args.cmd == 'search':
        client = TwitterClient(bearer_token=args.bearer_token)
        gen = client.search_recent(
            query=args.query,
            limit=args.limit,
            max_results=args.max_results,
            start_time=args.start_time,
            end_time=args.end_time,
        )

        # fan-out to selected sinks
        if args.jsonl:
            to_jsonl(args.jsonl, gen)
        elif args.csv:
            to_csv(args.csv, gen)
        elif args.sqlite:
            to_sqlite(args.sqlite, args.table, gen)
        else:
            # default: print first 20 to stdout (preview)
            from itertools import islice
            import json
            for row in islice(gen, 20):
                print(json.dumps(row, ensure_ascii=False, default=str))

if __name__ == '__main__':
    main()