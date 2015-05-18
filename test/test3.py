import os
import sys


class A():
    result = {}

    def __init__(self):
        # self.result = self.result
        pass

    def run(self):
        self.result['fsdf'] = 123


a = A()
a.run()

b = A()

print b.result