# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 11:25:34 2024

@author: Kevin
"""

from modules.prep import MeasurementObj

"""
vars(obj):

Returns the __dict__ attribute of an object, which contains the object's namespace (attributes and their values).

dir(obj):

Returns a list of valid attributes for the specified object, including attributes, methods, and special methods.
"""

# Ask user input to get a path to datafile(using Measurement1 abbreviation)
# file path could also be inserted as a manual string path into the initialization argument: M1 = MeasurementObj(file_path)
M1 = MeasurementObj()
#M2 = MeasurementObj()

