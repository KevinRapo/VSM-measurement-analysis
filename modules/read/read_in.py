# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 11:26:32 2024

@author: Kevin
"""

import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from scipy.interpolate import interp1d
from scipy.signal import argrelextrema
import copy
import traceback
from modules import global_variables  as G


#-------------- OPENING THE FILE AND INDEXING IT -------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------


    
def FilePathAndcwd():
    """
    Ask for user input for a datafile and creates global variables for file path and current directory.

    Returns
    -------
    file_path : STRING
        File path for the measurement file

    """
    
    root = tk.Tk()
    root.wm_attributes('-topmost', 1)
    root.withdraw()
    
    G.FILE_PATH = filedialog.askopenfilename()
    G.USER_PATH = os.getcwd()
    
    return None


def readDatafile(file_path):
    '''
    Reads in the data file and separates the header and measurement info into pandas dataframes.
    
    Parameters
    ----------
    file_path : STRING
        file path for the measurement file

    Returns
    -------
    header : PANDAS DATAFRAME
        header info   
    data : PANDAS DATAFRAME
        measurement data

    '''
    #Opens the selected data file
    with open(file_path, 'r') as f:
        i = 0 #Rowindex, how many rows until header 
        
        for line in f:
            i += 1
            if '[Data]' in line:
                f.close()
                break
    
         
    header = pd.read_csv(file_path, nrows = i , index_col = 2, encoding = 'ANSI',names = ['1','2','3','4'], on_bad_lines = 'skip')
    data = pd.read_csv(file_path, skiprows = i, header = 0, encoding = "ANSI")
    data = data[data["Transport Action"] == 1]
    
    return header, data

 
def determineDatafileType(header):
    """
    Determine if its VSM or ACMS datafile.
    
    Headers of VSM and ACMS files are similiar. DATA columns of those files have a difference in the Moment column. 
    In VSM the column is named Moment (emu), while in ACMS its named DC Moment (emu)

    Parameters
    ----------
    header : PANDAS DATAFRAME
        Measurement file header

    Returns
    -------
    token : STRING
        Data file type, "VSM" or "ACMS"

    """
    global option_specific_line
    token = "error - unknown datafile format"
    
    option_specific_line = header.iloc[1, 0]
    
    if "VSM" in option_specific_line:
        print("\nThis is a VSM data file \n")
        token = "VSM"
        
    elif "ACMS" in option_specific_line:
        print("\nThis is an ACMS data file \n")
        token = "ACMS"
        
    return token
    
    
def headerValueCheck(header, sample_property):
    """
    Text parsing function to return sample property value and unit from the header if they exist.
    
    Uses a helper function extractFloatWithUnit to parse the property.
    
    Parameters
    ----------
    header : PANDAS DATAFRAME
        measurement file header.
    sample_property : STRING
        PROPERTY TO CHECK.

    Returns
    -------
    float_val : TYPE
        description.
    unit : TYPE
        DESCRIPTION.
        
        
    None : Retuns None if no match found
    """
    
    header_column = header['2']

    print(f"Checking:{sample_property}, {header_column[sample_property]}")
    
    if not isinstance(header_column[sample_property], str) and np.isnan(header_column[sample_property]): #Checks whether the value is not a string and if it is a nan value
        print(f"NO VALID VALUE FOR {sample_property}, value is NAN \n")
        return None
    
    def extractFloatWithUnit(string):
        """
        Text parsing helper function to help with sample properties, uses regex to separate the input string into
        a (float, unit) format if it has units, if no units (float, None) format, if no value (None)
        
        Parameters
        ----------
        string : STRING
            the parameter string to examine.

        Returns
        -------
        float_val : FLOAT
            sample parameter value.
        unit : STRING
            sample parameter unit.
            
            
        None : Returns None if no match found
        """

        regex = r'^([\d.]+)\s*([a-zA-Z]+(\d)?)?$'
        match = re.search(regex, string)
        
        if match:
            float_str = match.group(1)
            unit = match.group(2)
            float_val = float(float_str)
            print(f"SAMPLE MASS :{float_val}, {unit}")
            return (float_val, unit)
        else:
            return None
        
    match = extractFloatWithUnit(header_column[sample_property])
    
    if match is None: #condition for extract_float_with_unit when it didn't find a match for a desired format therefore being a string
        print(f"{sample_property} had an input put it is not in the valid format: {header_column[sample_property]} \n")
        return None
    
    float_val = match[0]

    unit = match[1]

    
    return float_val, unit
  

def getMassInGrams(header):
    """
    Returns parsed MASS from Header

    Parameters
    ----------
    header : PANDAS DATAFRAME
        Measurement file header

    Returns
    -------
    mass : FLOAT
        Mass in grams.

    """
    
    #If the mass > 1, indicating that it's input is in mg, divides it by a 1000 to get g
    parameter = "SAMPLE_MASS"
    
    mass_unit = headerValueCheck(header, parameter)

    
    if mass_unit is None:
        return None
    
    mass = mass_unit[0]
    unit = mass_unit[1]
    
    if unit == 'g':
        return mass
    
    if unit == 'mg':
        return mass/1000
    
    if unit is None and mass > 1:
        mass= mass/1000
        print(f'Sample mass is {mass:.5f} grams \n')
        
    return mass


#Parsed sample size
def getAreaCM2(header):
    """
    Returns parsed area if it's in the header

    Parameters
    ----------
    header : PANDAS DATAFRAME
        Measurement file header.

    Returns
    -------
    area : FLOAT
        Area value
    
    None : Returns None if no match
    """
    #If the mass > 1, indicating that it's input is in mg, divides it by a 1000 to get g
    parameter = "SAMPLE_SIZE"
    
    area_unit = headerValueCheck(header, parameter)

    if area_unit is None:
        return None
    
    area = area_unit[0]
    unit = area_unit[1]
    
    if unit == "mm2":
        area = area/100
        unit = "cm2"
        
    print(f'Sample size is {area:.5f} {unit} \n') 
    return area
    

# ei tea kas päris nii ikka teha
#Parsed thickness
def getThickness(data):
    """
    Checks if the datafile title (from the header) contains the sample thickness,
    usually not there but just in case does the control.

    Parameters
    ----------
    data : PANDAS DATAFRAME
        Measurement file header

    Returns
    -------
    float_val : FLOAT
        Thickness value
    None : Return None if no match

    """
    #Checks whether the title contains sample thickness in nm units: e.g. "25nm" and outputs 25
    try:
        thickness = data.iloc[3,1] #Title index in table
        pattern = r"(\d+)\s*(nm)"
        match = re.search(pattern,thickness)
        
        if match:
            float_str = match.group(1)
            print(f"Checking thickness: {float_str} nm")
            float_val = float(float_str)*10**-7 # nm to cm conversion
            print(f"Sample thickness is: {float_val} cm \n" )
            
            return float_val
        
        else:
            print("Sample thickness not found in title \n")
            return None
    except:
        print("Sample thickness unknown Exeption \n")
        return None