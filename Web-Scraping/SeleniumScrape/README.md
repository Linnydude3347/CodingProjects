# Scrape with Selenium WebDriver

A minimal toolkit to scrape web pages using **Selenium 4** with Chrome or Firefox, powered by `webdriver-manager` (no manual driver installs). Includes a demo scraper for `quotes.toscrape.com`, CLI, and CSV/JSONL output.

## Features
- Chrome **or** Firefox WebDriver (auto-managed drivers)
- Headless mode (default), custom window size & user agent via `.env`
- Robust waits with `WebDriverWait` to avoid flakiness
- CLI demo: scrape quotes + pagination
- Output to **JSONL** or **CSV**

## Quickstart
```bash
cd selenium_scraper
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # optional: tweak HEADLESS/BROWSER/etc
```

Run the demo (prints first 20 unless you save to a file):
```bash
python -m scrape_selenium.cli quotes --max-pages 3
```

Save to JSONL:
```bash
python -m scrape_selenium.cli quotes --max-pages 5 --jsonl data/quotes.jsonl
```

Save to CSV:
```bash
python -m scrape_selenium.cli quotes --max-pages 5 --csv data/quotes.csv
```

## Configuration (.env)
```env
HEADLESS=true
BROWSER=chrome        # or firefox
WINDOW_SIZE=1280,800
USER_AGENT=
```

## Extending
- Add a new function in `scrape_selenium/scraper.py` that navigates, waits for target elements, and yields dicts.
- Wire it into the CLI in `scrape_selenium/cli.py` as another subcommand.
- Use `outputs.to_jsonl` or `outputs.to_csv` to persist results.

## Notes
- You need a recent Chrome **or** Firefox installed locally. `webdriver-manager` will download the matching driver.
- In some Linux headless environments you may need extra system libs; consider a slim Selenium Docker image if needed.