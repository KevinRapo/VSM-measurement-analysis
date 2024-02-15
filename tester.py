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

# %%


class MyClass:
    class_variable = 42

    @staticmethod
    def static_method():
        # Attempting to modify class_variable inside a static method
        # This line will not raise an error, but it's not a recommended practice
        MyClass.class_variable = 100
        return "Class variable modified inside static method"


# Accessing the static method
# Output: Class variable modified inside static method
print(MyClass.static_method())

# Accessing the class variable
print(MyClass.class_variable)  # Output: 100
# %%


class MyClass:
    @classmethod
    def my_method(cls, arg):
        print(f"Class method called with {arg}")

# Call the class method on the class
MyClass.my_method("class")

# Call the class method on an instance
obj = MyClass()
obj.my_method("instance")

