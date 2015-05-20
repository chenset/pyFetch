import os
import sys


class A():
    cls_a = {}

    def __init__(self):
        self.instance_a = {}
        pass


a = A()
print a.__dict__

print A.__dict__