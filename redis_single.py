import redis


class Redis:
    instance = None
    redis = None

    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=1)

    @staticmethod
    def get():
        return Redis.get_instance().redis

    @staticmethod
    def get_instance():
        if Redis.instance is None:
            Redis.instance = Redis()

        return Redis.instance