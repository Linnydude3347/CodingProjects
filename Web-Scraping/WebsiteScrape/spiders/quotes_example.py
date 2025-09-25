import scrapy
from datetime import datetime

class QuotesSpider(scrapy.Spider):
    name = "quotes_demo"
    start_urls = ["https://quotes.toscrape.com/"]

    def parse(self, response):
        for q in response.css(".quote"):
            yield {
                "text": q.css(".text::text").get(),
                "author": q.css(".author::text").get(),
                "tags": q.css(".tag::text").getall(),
                "url": response.url,
                "fetched_at": datetime.utcnow().isoformat(),
            }
        # pagination
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)