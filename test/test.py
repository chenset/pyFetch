class A:
    @classmethod
    def fun2(cls):
        cls.var = 2
        print cls.var

    def fun3(self):
        self.var = 3
        print self.var


a = A()

a.fun2()
a.fun3()


a.fun2()
a.fun3()
a2 = A()
a2.fun3()

a2 = A()
a2.fun3()

a2 = A()
a2.fun3()

a2 = A()
a2.fun3()

a2 = A()
a2.fun3()

print A.var