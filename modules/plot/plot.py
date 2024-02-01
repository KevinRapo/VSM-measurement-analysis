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

def plotMvsH(separated_pairs):
    """
    Plots the MvsH measurement pictures wtih a legend where it specifies the ascending and descending part with different shades.
    Plots the original field and true field values separately with different colors.
    
    It also saves the figures in the same folder the measurement file is in.

    Parameters
    ----------
    separated_pairs : DICT OF {float : list of list of dataframes}
        Dictionary with MvsH measurements, temp_values : measurement_dataframes format.

    Returns
    -------
    Direct return None but saves the plots in a dedicated folder.

    """
    #Plots the MvsH measurement pair with different colors
        
    i_pair = 1
        
    for df in separated_pairs:
        
        colorIdx = df[0].iloc[1].name
        Color = ORIGINAL_DATAFRAME["color"].loc[colorIdx]
        
        fig, ax = plt.subplots()
        H1 = df[0]["Magnetic Field (Oe)"]
        M1 = df[0]["Moment (emu)"]
        H2 = df[1]["Magnetic Field (Oe)"]
        M2 = df[1]["Moment (emu)"] 
        
        ax.plot(H1 ,M1, color = "grey", label = "Descending")#!!! mis siin värvidega jääb
        ax.plot(H2, M2, color = "grey", label = "Ascending")
        
        if "True Field (Oe)" in df[0]:
            
            H1_true = df[0]["True Field (Oe)"]
            H2_true = df[1]["True Field (Oe)"]   
            ax.plot(H1_true, M1, color = Color, label = "True Field Descending", alpha = 0.5)
            ax.plot(H2_true, M2, color = Color, label = "True Field Ascending")
        
        plot_title = f"M vs H at {const} K"
        ax.set_title(plot_title)
        ax.set_xlabel("Magnetic field (Oe)")
        ax.set_ylabel("Moment (emu)")
        ax.legend() #Hetkel legend nimetab selle järgi et esimene tsükkel on kasvav ja teine kahanev ehk eeldus et mõõtmisel temp algas kasvamisest
        ax.grid(True)

        fig.savefig(os.path.join(folder_name,f'MvsH_graph_at_{const}K_{i_pair}.png'),bbox_inches = "tight", dpi = 200) #PC
        i_pair = i_pair + 1
        plt.show()
        
    return None

def plotMvsT(separated_pairs, const):
    """
    Plots the separated_pairs measurement pictures wtih a legend where it specifies the ascending and descending part with different shades.
    
    If there are multiple measurements on the same field, plots them on the same graph.
    It also saves the figures in the same folder the measurement file is in.
    
    Parameters
    ----------
    separated_pairs : LIST OF LIST OF DATAFRAMES
        Nested list with MvsT measurements.

    Returns
    -------
    Direct return None but saves the plots in a dedicated folder.

    """
   
    fig, ax = plt.subplots()
    i_pair = 1

    for pair in separated_pairs:

        
        T1 = pair[0]["Temperature (K)"]
        M1 = pair[0]["Moment (emu)"]
        T2 = pair[1]["Temperature (K)"] if len(pair) > 1 else None
        M2 = pair[1]["Moment (emu)"] if len(pair) > 1 else None
        
        colorIdx = pair[0].iloc[0].name
        Color = ORIGINAL_DATAFRAME["color"].loc[colorIdx]
        
        ax.plot(T1,M1,color = Color, label = f"Ascending {i_pair}", alpha = 0.5) # peaks tegelt kontrollima kas kasvab või kahaneb
        ax.plot(T2,M2,color = Color, label = f"Descending {i_pair}") if len(pair) > 1 else None #, marker = "o") #descending ei pea paika kui on alt üle > alt üles mõõtmine
        ax.set_title(f"M vs T at {const} Oe")
        ax.set_xlabel("Temperature (K)")
        ax.set_ylabel("Moment (emu)")
        ax.legend() #Hetkel legend nimetab selle järgi et esimene tsükkel on kasvav ja teine kahanev ehk eeldus et mõõtmisel temp algas kasvamisest
        ax.grid(True)
        i_pair = i_pair + 1
        
    fig.savefig(os.path.join(folder_name,f'MvsT_graph_at_{const}K.png'),bbox_inches = "tight", dpi = 200)
    plt.show()
    
    return None

def plotMeasurementTimeseries():
    """
    Plots temperature, field and moment against time based on the colors they have in the original dataframe.

    Returns
    -------
    None.

    """
    
    # Create subplots with shared x-axis
    fig, axes = plt.subplots(nrows=3, sharex=True)
    
    # Plot data on each subplot
    time_axis = "Time Stamp (sec)"
    ORIGINAL_DATAFRAME.plot(x=time_axis, y="Temperature (K)", kind="scatter", c=ORIGINAL_DATAFRAME["color"].values, ax=axes[0])
    ORIGINAL_DATAFRAME.plot(x=time_axis, y="Magnetic Field (Oe)", kind="scatter", c=ORIGINAL_DATAFRAME["color"].values, ax=axes[1])
    ORIGINAL_DATAFRAME.plot(x=time_axis, y="Moment (emu)", kind="scatter", c=ORIGINAL_DATAFRAME["color"].values, ax=axes[2])
    
    # Customize axes labels and other properties
    
    axes[0].set_ylabel("Temperature (K)", fontsize = 8)
    axes[1].set_ylabel("Magnetic Field (Oe)", fontsize = 8)
    axes[1].tick_params(axis = "y", labelsize = 8)
    axes[2].set_ylabel("Moment (emu)", fontsize = 8)
    axes[-1].set_xlabel("Time Stamp (sec)")
    fig.suptitle("Timeseries \n (black dots are discarded from individual plots)", fontsize = 10)
    
    fig.savefig(os.path.join(folder_name,'timeseries.png'),bbox_inches = "tight", dpi = 200)
    
    # Show the plot
    plt.show()
    