import pymongo


class Mongo:
    instance = None
    conn = None
    cursor = None

    def __init__(self):
        self.conn = pymongo.MongoClient("127.0.0.1", 27017).test
        self.conn.parsed.ensure_index('url_md5', unique=True)
        self.conn.queue.ensure_index('url_md5', unique=True)

    @staticmethod
    def get():
        if Mongo.instance is None:
            Mongo.instance = Mongo()

        return Mongo.instance.conn

