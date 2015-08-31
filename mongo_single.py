import pymongo


class Mongo:
    instance = None
    conn = None
    cursor = None

    def __init__(self):
        self.conn = pymongo.MongoClient("127.0.0.1", 27017).pyfetch

    @classmethod
    def get(cls):
        if cls.instance is None:
            cls.instance = cls()

        return cls.instance.conn

