from datetime import datetime
from pymongo import MongoClient, ASCENDING

class MongoPipeline:
    def __init__(self, uri, db_name, collection, unique_key):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection
        self.unique_key = unique_key or "url"
        self.client = None
        self.coll = None

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        return cls(
            uri=s.get('MONGO_URI', 'mongodb://localhost:27017'),
            db_name=s.get('MONGO_DB', 'scrapy_db'),
            collection=s.get('MONGO_COLLECTION', 'pages'),
            unique_key=s.get('MONGO_UNIQUE_KEY', 'url'),
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.uri)
        db = self.client[self.db_name]
        self.coll = db[self.collection_name]
        # Ensure unique index
        if self.unique_key:
            self.coll.create_index([(self.unique_key, ASCENDING)], unique=True)

    def close_spider(self, spider):
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        data = dict(item)
        data.setdefault('fetched_at', datetime.utcnow())
        if self.unique_key and self.unique_key in data:
            self.coll.update_one(
                {self.unique_key: data[self.unique_key]},
                {'$set': data},
                upsert=True
            )
        else:
            self.coll.insert_one(data)
        return item