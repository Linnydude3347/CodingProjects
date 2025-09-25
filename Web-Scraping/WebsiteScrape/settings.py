import os
from dotenv import load_dotenv
load_dotenv()  # load .env if present

BOT_NAME = "scrape_mongo"

SPIDER_MODULES = ["scrape_mongo.spiders"]
NEWSPIDER_MODULE = "scrape_mongo.spiders"

# Respect robots.txt by default; change to False if you have permission and need to ignore.
ROBOTSTXT_OBEY = True

# Concurrency & politeness
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 0.25

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
}

DOWNLOADER_MIDDLEWARES = {
    "scrape_mongo.middlewares.RandomUserAgentMiddleware": 400,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 550,
}

# Mongo configuration (can be overridden via environment)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "scrapy_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "pages")
MONGO_UNIQUE_KEY = os.getenv("MONGO_UNIQUE_KEY", "url")

ITEM_PIPELINES = {
    "scrape_mongo.pipelines.MongoPipeline": 300,
}

FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")