import scrapy
from urllib.parse import urlparse
from datetime import datetime
from ..items import PageItem

class GenericSpider(scrapy.Spider):
    name = "generic"

    def __init__(self, url=None, allowed=None, follow="true", max_pages=100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not url:
            raise ValueError("Provide a start URL: -a url=https://example.com")
        self.start_urls = [url]
        self.follow = (str(follow).lower() in ("true", "1", "yes", "y"))
        try:
            self.max_pages = int(max_pages)
        except Exception:
            self.max_pages = 100
        self.pages_seen = 0

        if allowed:
            self.allowed_domains = [allowed]
        else:
            # derive domain from the start URL to keep crawl constrained
            netloc = urlparse(url).netloc
            if netloc:
                self.allowed_domains = [netloc]

    def parse(self, response):
        self.pages_seen += 1

        item = PageItem()
        item["url"] = response.url
        item["status"] = response.status
        item["title"] = (response.css("title::text").get() or "").strip()
        item["description"] = (response.css('meta[name="description"]::attr(content)').get() or "").strip()
        item["h1"] = (response.css("h1::text").get() or "").strip()
        item["content_length"] = len(response.text or "")
        # simple preview of body text
        paras = [p.strip() for p in response.css("p::text").getall() if p.strip()]
        preview = " ".join(paras)[:400]
        item["text_preview"] = preview
        item["fetched_at"] = datetime.utcnow()
        yield item

        if self.follow and self.pages_seen < self.max_pages:
            # Follow links within the same domain
            for href in response.css("a::attr(href)").getall():
                next_url = response.urljoin(href)
                # Let Scrapy's dupefilter avoid repeats; we simply yield requests
                yield scrapy.Request(next_url, callback=self.parse)