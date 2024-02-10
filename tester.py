# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 20:54:11 2024

@author: Kevin
"""
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

#%%

class MyClass:
    class_variable = 42

    @staticmethod
    def static_method():
        # Attempting to modify class_variable inside a static method
        MyClass.class_variable = 100  # This line will not raise an error, but it's not a recommended practice
        return "Class variable modified inside static method"

# Accessing the static method
print(MyClass.static_method())  # Output: Class variable modified inside static method

# Accessing the class variable
print(MyClass.class_variable)  # Output: 100
