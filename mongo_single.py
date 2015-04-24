import pymongo


class DB:
    instance = None
    conn = None
    cursor = None

    def __init__(self):
        self.conn = pymongo.MongoClient("172.16.16.16", 27017).test

    @staticmethod
    def get():
        if DB.instance is None:
            DB.instance = DB()

        return DB.instance.conn

print pymongo.MongoClient("172.16.16.16", 27017).test.mycoll.find_one()
