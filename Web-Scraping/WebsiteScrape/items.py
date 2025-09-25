import scrapy

class PageItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    h1 = scrapy.Field()
    status = scrapy.Field()
    content_length = scrapy.Field()
    text_preview = scrapy.Field()
    fetched_at = scrapy.Field()