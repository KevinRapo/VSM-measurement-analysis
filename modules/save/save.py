# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 11:26:33 2024

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

# Siin on ka üks huvitav error kui file excelis avatud sama aeg siis ei luba uut üle salvestada
def appendAndSave(separated_pairs, data_type):
    """
    Appends the separate pair parts back into one after all the processing and saves them to a csv file

    Parameters
    ----------
    separated_pairs : LIST OF LIST OF DATAFRAME
        All the measurement pairs in dataframe pairs.
    data_type : STRING
        Measurement type.

    Returns
    -------
    None.

    """
    
    i_pair = 1
    for pair in separated_pairs:
        
        result = pd.concat([pair[0], pair[1].tail(pair[1].shape[0]-1)])
        
        file_name = f'{data_type}_data_at_{const}_{i_pair}.csv'
        
        full_path = os.path.join(folder_name, file_name)
        
        result.to_csv(full_path, index = False)
        
        i_pair = i_pair + 1
            
    return None