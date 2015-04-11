import pybloomfilter


class BLMatched:
    instance = None
    bl = None

    def __init__(self):
        self.bl = pybloomfilter.BloomFilter(500000000, 0.1, './url_matched.bloom')

    @staticmethod
    def get():
        return BLMatched.get_instance().bl

    @staticmethod
    def get_instance():
        if BLMatched.instance is None:
            BLMatched.instance = BLMatched()

        return BLMatched.instance