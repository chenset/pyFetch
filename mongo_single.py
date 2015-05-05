import pymongo


class Mongo:
    instance = None
    conn = None
    cursor = None

    def __init__(self):
        self.conn = pymongo.MongoClient("127.0.0.1", 27017).test

    @classmethod
    def get(cls):
        if cls.instance is None:
            cls.instance = Mongo()

        return cls.instance.conn

