# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 20:54:11 2024

@author: Kevin
"""

from modules import prep as P

#obj = P.setPointsColor_("Kevin")
P.setPointsColor_.hello(2)
#%%
class MyClass:
    index = 0
    @staticmethod
    def regular_method():
        MyClass.index += 1
        return None


# obj = MyClass()
# print(obj.regular_method())
MyClass.regular_method()
MyClass.regular_method()
# Try to call the regular method without an instance
print(MyClass.index)  # Raises an error

