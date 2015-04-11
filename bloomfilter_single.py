import pybloomfilter


class BL:
    instance = None
    bl = None

    def __init__(self):
        self.bl = pybloomfilter.BloomFilter(500000000, 0.1, './url.bloom')

    @staticmethod
    def get():
        return BL.get_instance().bl

    @staticmethod
    def get_instance():
        if BL.instance is None:
            BL.instance = BL()

        return BL.instance