# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 13:45:38 2023

@author: kevin
"""

import os
import re
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt

#-------------- OPENING THE FILE AND INDEXING IT -------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
root = tk.Tk()
root.wm_attributes('-topmost', 1)
root.withdraw()

file_path = filedialog.askopenfilename()

#Opens the selected data file
with open(file_path, 'r') as f:
    i = 0 #Rowindex, how many rows will get_header read in
    for line in f:
        i += 1
        if '[Data]' in line:
            break

#--------------READING IN THE HEADER DATA-----------------------------------------------------------------------------------


def get_header(dataFile):
    #reads in i amount of rows from the data file, i indicating the number
    #of lines from the header to the data section
    header = pd.read_csv(dataFile, nrows = i , index_col = 2, encoding = 'ANSI',names = ['1','2','3','4'], on_bad_lines = 'skip')
    return header

#Lines 0-i from the file
data_header = get_header(file_path)

#Sample mass from data header
SAMPLE_MASS = data_header['2']['SAMPLE_MASS']
SAMPLE_MASS_NAME = "SAMPLE_MASS"



def extract_float_with_unit(string):
    #extract_float_with_unit function uses regex to index the input string
    #into a (float, unit) format if it has units, if no units (float, None) format, if no value (None)
    regex = r'^([\d.]+)\s*([a-zA-Z]+(\d)?)?$'# regular expression to match float value and unit
    match = re.search(regex, string)
    if match:
        float_str = match.group(1)
        unit = match.group(2)
        float_val = float(float_str)
        return (float_val, unit)
    else:
        return None

def header_value_check(info, name):
    #header_value_check checks the value of interest, is the value nan or is it just a string in 
    #the wrong format, otherwise outputs the float value
    print(f"Checking: {name}, {info}")#Hetkel jääb
    if not isinstance(info, str) and np.isnan(info): #Checks whether the value is not a string and if it is a nan value
        print(f"NO VALID VALUE FOR {name}, value is NAN \n")
        return None
    match = extract_float_with_unit(info)
    if match is None: #condition for extract_float_with_unit when it didn't find a match for a desired format therefore being a string
        print(f"{name} had an input put it is not in the valid format: {info} \n")
        return None
    float_val = match[0]
    #print("float value:", float_val)#Hetkel jääb
    unit = match[1]
    #print("units:", unit)#Hetkel jääb
    return float_val, unit #Ühikutega peaks veel midagi tegema

header_mass = header_value_check(SAMPLE_MASS, SAMPLE_MASS_NAME)

def get_mass(mass):
    #If the mass > 1, indicating that it's input is in mg, divides it by a 1000 to get g
    if mass is None:
        return None
    val = mass[0] #Mass value
    if val > 1:
        val= val/1000
        print(f'Sample mass is {val:.5f} grams \n')
    return val

mass = get_mass(header_mass)

PdStd_susceptibility = 5.25*10**-6 #(emu/Oe*g)

#----------------------READING IN AND PREPROCESSING THE MEASUREMENT DATA-------------------------------------------------

def get_measurements(dataFile):
    #get_measurements function reads in the rest of the data under the [Data] line and formats it as a table
    measurements = pd.read_csv(dataFile, skiprows = i, header = 0, encoding = "ANSI")
    return measurements

#Forms a table from the measurement data and excludes all lines that contain 2 in the "Transport Action" column
data_measurements = get_measurements(file_path)[(get_measurements(file_path)["Transport Action"] != 2) & \
                                                pd.notna(get_measurements(file_path)["Transport Action"])]


field = data_measurements["Magnetic Field (Oe)"]

moment = data_measurements["Moment (emu)"]

true_field = moment/(PdStd_susceptibility*mass)
true_field.name = "True Field (Oe)"

pd_table = pd.concat([field, true_field], axis=1)
pd_table["Field correction"] = field-true_field

val = pd_table["Magnetic Field (Oe)"]

#-----
def round_H_to_even_round_number(val):
    number = max(val)
    if number >= 10000:
        return round(number / 1000) * 1000
    elif number >= 1000:
        return round(number / 100) * 100
    elif number >= 100:
        return round(number / 10) * 10
    else:
        return round(number)

max_range = round_H_to_even_round_number(val)
print("Range:",max_range)


pd_table.to_csv(os.path.join(os.getcwd(),f"PdCorrection tables\\PdCal_{max_range}_Oe.csv"))


plt.plot(pd_table["Magnetic Field (Oe)"], pd_table["Field correction"], "-o")
plt.title(f"Corretion vs Field at {max_range} Oe")
plt.xlabel("Magnetic Field (Oe)")
plt.ylabel("Correction")

plt.savefig(os.path.join(os.getcwd(),f"PdCorrection tables\\PdCal_{max_range}_Oe.png"),
                         dpi = 300,
                         bbox_inches = "tight")

















