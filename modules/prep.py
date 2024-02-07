# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 11:26:32 2024

@author: Kevin
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import argrelextrema

#------------------------------------------Data classification-----------------------------


def checkMeasurementType2(measurement_table, discrete_detection_ration = 0.02, min_count = 5):
    """
    Recognizes what measurement types are present in the file.
    
    Returns the temperatures and magnetic fields where the MvsH and MvsT measurements were made

    Parameters
    ----------
    measurement_table : PANDAS DATAFRAME
        Measurement file data.
    discrete_detection_ration : FLOAT, optional
        Discrete detection ratio. The default is 0.02.
    min_count : INT, optional
        Min amount of instances of a measurement to pass the level!?. The default is 5.

    Returns
    -------
    temperatures_of_interest : PANDAS SERIES
        MvsH measurement temperatures.
    magnetic_fields_of_interest : PANDAS SERIES
        MvsT measurement fields.

    """
    global tempCount
    #Checks what measurements the file contains
    
    rounded_dataset_T = measurement_table["Temperature (K)"].round(decimals=1)
    rounded_dataset_H = measurement_table["Magnetic Field (Oe)"]#.round(decimals=0)
    
    #returnitavad Seried
    magnetic_fields_of_interest = pd.Series(dtype=float)
    temperatures_of_interest = pd.Series(dtype=float)
    
    
    tempCount = rounded_dataset_T.value_counts()
    fieldCount = rounded_dataset_H.value_counts()
    
    # tempCount = tempCount[tempCount > min_count]
    # fieldCount = fieldCount[fieldCount > min_count]
    
    codes_T, uniques_T = pd.factorize(rounded_dataset_T)
    codes_H, uniques_H = pd.factorize(rounded_dataset_H)
    
    ratio_T = uniques_T.size/rounded_dataset_T.size
    ratio_H = uniques_H.size/rounded_dataset_H.size
    print(f"T : {ratio_T}, H : {ratio_H }")
    
    
    if ratio_T < discrete_detection_ration: #discrete
    
        if ratio_H < discrete_detection_ration: #discrete

            print("T discrete, H discrete = error \n")
        
        else: #continous
        
            print("T discrete, H continous = MvsH \n")
            temperatures_of_interest = pd.concat([temperatures_of_interest,pd.Series(tempCount.index.values)], ignore_index = True)
            
    else: #continous
    
        if ratio_H < discrete_detection_ration: #discrete

            print("T continous, H discrete = MvsT \n")
            fieldCount = fieldCount[fieldCount > min_count]
            magnetic_fields_of_interest = pd.concat([magnetic_fields_of_interest,pd.Series(fieldCount.index.values)], ignore_index = True)
        else: #continous

            print("T continous, H continous = both \n")
            
            meanTempCount=tempCount.mean()                     #see osa siin annab segafailide puhul mõistlikud numbrid. Aga mõne erilisema faili korral ei saa ta aru et sega fail on, aga need read annavad ka siis mõistlikud numbrid. Äkki saame kuidagi hoopis neid prinditavaid liste kasutada faili ära tundmiseks.
            muutuja = rounded_dataset_T.value_counts() > meanTempCount*10
            temperatures_of_interest = pd.Series(rounded_dataset_T.value_counts()[muutuja].index.values)
            print("meanTempCount",meanTempCount)
            meanFieldCount=fieldCount.mean()
            muutuja2 = rounded_dataset_H.value_counts() > meanFieldCount*10
            magnetic_fields_of_interest = pd.Series(rounded_dataset_H.value_counts()[muutuja2].index.values)
            
    return temperatures_of_interest, magnetic_fields_of_interest

#----------------------------------------MvsH specific functions-------------------------

def getMeasurementMvsH(original_dataframe, value, bound = 1):
    """
    Saves the initial row indices of data point values that fall between the MvsH bound from the constant temperature points for further filtering.
    Returns them in a nested list.

    Parameters
    ----------
    value : FLOAT
        Measurement temperature.
    bound : FLOAT, optional
        The plus/min bound from the constant value to choose elements by. The default is 1.

    Returns
    -------
    indices : LIST OF INT
        Nested list with int indices at each const temp bound.

    """
    #Saves all the indices of the points that fall between the bound
    table = original_dataframe[['Temperature (K)', "color"]]
    lower = value - bound
    upper = value + bound
    filtered_df = table[(table['Temperature (K)'] >= lower) & (table['Temperature (K)'] <= upper) & (table['color'] == "black") ]
    indices = filtered_df.index.tolist()
        
    return indices


def removeBleedingElement(pairs):
    """
    This function ensures that there is no value "bleeding" from the next pair due to the way
    separationIndexForSingleSeries function slices multiple measurements made on the same const value.
    
    Special case when the first element from the next measurement "bleeds" into the previous measurement,
    the function uses a ratio = first_part_max/second_part_max to determine if the first and second part
    have the same max value and removes the second part last element if the ratio is out of bounds.
    
    Parameters
    ----------
    pairs : LIST OF LIST OF DATAFRAMES
        Nested list with dataframe pairs for the measurements.

    Returns
    -------
    new_pairs : LIST
        "pairs" list with removed elements, if there were any to remove.

    """

    new_pairs = []

    for pair in pairs:
        
        first = pair[0]
        
        second = pair[1]
        
        # try:
        first_max = max(first["Magnetic Field (Oe)"])
        second_max = max(second["Magnetic Field (Oe)"])
        ratio = first_max/second_max
        # except ValueError:
        #     error_message = "Change separationIndexForSingleSeries argument n for correct extrema points"
        #     showExtremaError(error_message)
        
        new_list = []

        while not 0.9 < ratio < 1.1:
            if ratio < 0.9:

                second = second[:-1]
                ratio = first_max/max(second["Magnetic Field (Oe)"])
                
            elif ratio > 1.1:

                second = second[:-1]
                break

        new_list.append(first)
        new_list.append(second)
        new_pairs.append(new_list)
        
    return new_pairs

def roundFieldForCorrection(pairs):
    """
    Returns the max field value for each individual MvsH measurement pair for correction fit

    Parameters
    ----------
    pairs : LIST OF LIST OF DATAFRAMES
        Nested list with dataframe pairs for the measurements.

    Returns
    -------
    values : LIST OF INT
        List with max field values for each measurement.

    """
    #rounds the magnetic field to a nice number (100041.221 -> 100000)
    values = []
    for pair in pairs:
        first_max = max(pair[0]["Magnetic Field (Oe)"])
        second_max = max(pair[1]["Magnetic Field (Oe)"]) if len(pair[1]) >= 1 else None
        max_range = None
        
        #print(f"{first_max=}")
        #print(f"{second_max=}")
        
        if second_max is not None:
            if first_max > second_max:
                max_range = first_max
            elif first_max < second_max:
                max_range = second_max
        else:
            max_range = first_max
            
        if max_range >= 10000:
            nr = round(max_range / 1000) * 1000
        elif max_range >= 1000:
            nr = round(max_range / 100) * 100
        elif max_range >= 100:
            nr = round(max_range / 10) * 10
        else:
            nr = round(max_range)
        values.append(nr)
        
    return values

def searchCorrectionTable(folder_path, number):
    """
    Searches for the correction table that is closest to the measurement max field value,
    returns the file path.

    Parameters
    ----------
    folder_path : STRING
        Folder path for the correction tables folder.
    number : INT
        Measurement max field value.

    Returns
    -------
            STRING
        File path for the closest correction table.

    """
    closest_match = None
    min_difference = float('inf')  # Initialize with positive infinity
    
    for filename in os.listdir(folder_path):
        parts = filename.split('_')  # Modify this based on your file naming convention
        try:
            value = int(parts[1])
            difference = abs(number - value)
            if difference < min_difference:
                min_difference = difference
                closest_match = filename
                
        except (ValueError, IndexError):
            # Ignore filenames that don't have a numeric part or invalid parts
            pass
        
    if closest_match:
        return os.path.join(folder_path, closest_match)
    else:
        return None

    


def CorrectionTableToDict(correctionField_values, user_path):
    """
    Returns the corresponding amount of correction tables for each unique min/max field value
    in a dictionary form with the key being the value the table is for.

    Parameters
    ----------
    correctionField_values : INT
        Correction field max values.

    Returns
    -------
    correction_tables : DICT OF {int : Dataframe}
        Dictionary with max_field_value : values_at_that_field format.

    """
    #returns the corresponding amount of correction tables for each unique min/max measurement value in a dictionary form with the key being the value the table is for
    correction_tables = {}
    correction_folder_path = os.path.join(user_path,'PdCorrection tables')
    
    for nr in correctionField_values:
        correction_table_path = searchCorrectionTable(correction_folder_path, nr)
        
        if correction_table_path is None:
            print(f"{nr} Oe jaoks ei leia parandustabelit ")
            continue
        correction_table_measurements = pd.read_csv(correction_table_path, index_col=0, encoding="ANSI")
        correction_tables[nr] = correction_table_measurements
        
    return correction_tables

def interpolateTrueField(magnetic_field_values, correction_tables):
    """
    Uses the correction table to interpolate the correct values for the measurement

    Parameters
    ----------
    magnetic_field_values : SERIES OF FLOAT
        One part of the measured MvsH field values.
    correction_tables : DATAFRAME
        Correction table in dataframe format.

    Returns
    -------
    true_field_interpolated : NUMPY.NDARRAY
        Interpolated correction values based on the measurement points.

    """
    x = correction_tables["Magnetic Field (Oe)"]
    y = correction_tables["True Field (Oe)"]

    # Create an interpolation function
    interp_func = interp1d(x, y, kind='linear', fill_value='extrapolate')

    # Call the interpolation function with magnetic_field_values to get the interpolated values
    true_field_interpolated = interp_func(magnetic_field_values)
    return true_field_interpolated

def interpolateMvsH(separated_MvsH, correction_tables):
    """
    Adds the true field values column to the existing measurement dataframes.

    Parameters
    ----------
    separated_MvsH : LIST OF LIST OF DATAFRAMES
        Nested list with MvsH measurements dataframes.
    correction_tables : DICT OF {int : Dataframe}
        Dict with the correction tables, field_value : values_at_that_field format.

    Returns
    -------
    interpolated_dict : LIST OF LIST OF DATAFRAMES
        "separated_MvsH" with the added true field column

    """

    interpolated_dict = {}
    for pair in separated_MvsH:
        
        # max_val = max(val_pair[0]["Magnetic Field (Oe)"]) # [0] ei pruugi alati õige max anda
        # print("max val",max_val)
        
        first_max = max(pair[0]["Magnetic Field (Oe)"])
        second_max = max(pair[1]["Magnetic Field (Oe)"]) if len(pair[1]) >= 1 else None
        max_range = None
        
        # print(f"{first_max=}")
        # print(f"{second_max=}")
        if second_max is not None:
            if first_max > second_max:
                max_range = first_max
            elif first_max < second_max:
                max_range = second_max
        else:
            max_range = first_max
            
        for key in correction_tables:
            if key - 200 <= max_range <= key + 200:

                #print(f"{max_range} kukub {key} vahemikku")
                
                for val in pair:
                    
                    magnetic_field_values = val["Magnetic Field (Oe)"]
                    # print(len(magnetic_field_values))
                    true_field_interpolated = interpolateTrueField(magnetic_field_values, correction_tables[key])
                    #print(type(true_field_interpolated))
                    # print(len(true_field_interpolated))
                    val["True Field (Oe)"] = true_field_interpolated
                                
    return interpolated_dict #!!! siin vaata üle func returnib aga ei omista muutujale

#-----------------------------MvsT specific functions--------------------------------

def getMeasurementMvsT(original_dataframe, const):
    """
    Saves the initial row indices of the MvsT measurement points that are equal to the const field value.

    Parameters
    ----------
    const : FLOAT
        The constant field value.

    Returns
    -------
    indices : LIST OF INT
        List with row indices at each const field

    """
    #Saves all the indices of the points that are equal to the predetermined H value
    # row_indices = {}
    # print(ORIGINAL_DATAFRAME)
    table = original_dataframe['Magnetic Field (Oe)']
    indices = table.index[table == const].tolist()
    # row_indices[const] = indices

    return indices

#---------------------------------------Universal functions that both paths use----------------------------------------------

#Separates all the series in the indices that grow by one and returns the longest one, that one being the measurement indices
def filterMeasurementIndices(unfiltered_indices):
    """
    Filters the measurement indices so that the longest consecutive list is the measurement.

    Parameters
    ----------
    unfiltered_indices : LIST OF INT
        List with unfiltered measurement data indices.

    Returns
    -------
    longest_sequence : LIST OF INT
        List with filtered measurement data indices.

    """
    
    consecutive_sequences = []
    current_sequence = [unfiltered_indices[0]]

    for i in range(1, len(unfiltered_indices)):
        if unfiltered_indices[i] - unfiltered_indices[i - 1] == 1:
            current_sequence.append(unfiltered_indices[i])
        else:
            if len(current_sequence) > 1:
                consecutive_sequences.append(current_sequence)
            current_sequence = [unfiltered_indices[i]]

    # Check if the last sequence is consecutive and has more than one element
    if len(current_sequence) > 1:
        consecutive_sequences.append(current_sequence)
    
    longest_sequence = max(consecutive_sequences, key=len, default=[])
    
    return longest_sequence


#Returns the separation indices for ascending and descending points based on the extrema
def separationIndexForSingleSeries(original_dataframe, indices, column_name, const, x = 0.1):# https://stackoverflow.com/questions/48023982/pandas-finding-local-max-and-min
    """
    Returns the indices of the series local peaks (maxima and minima) in a list

    Parameters
    ----------
    indices : SERIES OF INT.
        The series indices.
    column_name : STRING
        Name of the column to analyze based on the measurement.
    x : FLOAT
        Percentage parameter, determines the percentage of n (number of points to compare around the extrema) to use. 

    Returns
    -------
    min_max : LIST OF [pandas.Index(min), pandas.index(max)]
        The min and max indices of the extrema points
    """
    
    data = original_dataframe.loc[indices, column_name]
    
    # print("xxxxxxxxxxxxxxxxxxxx")
    # print(type(data))
    
    if isinstance(data, pd.Series):
        # Convert a Series to a DataFrame with a specified column name
        data = pd.DataFrame({column_name: data})
    
    # print("Test OK OK")
    # print("xxxxxxxxxxxxxxxxxxxx")
    # print(data)
    # print("xxxxxxxxxxxxxxxxxxxx")
    # print(type(data))
    # print("xxxxxxxxxxxxxxxxxxxx")
    # print(data.values)
    # print("xxxxxxxxxxxxxxxxxxxx")
    # print(data[column_name])
    # print("xxxxxxxxxxxxxxxxxxxx")
    # print(data[column_name].values)
    # print("xxxxxxxxxxxxxxxxxxxx")
    
    index = data.index
    
    n = int(x*len(data))
    #print(f"n for this run: {n}")
    
    # Find local peaks
    relative_min_indices = argrelextrema(data[column_name].values, np.less_equal, order=n)[0]
    relative_max_indices = argrelextrema(data[column_name].values, np.greater_equal, order=n)[0]
    
    min_indices = index[relative_min_indices]
    max_indices = index[relative_max_indices]
    
    title = ""
    
    def removeSpecialCaseIndex():
        """
        Helper function that removes the first min/max index if it's value is near 0 tesla
        because it is not needed from the data perspective. All the points from the first removed
        index till the next index will be removed from the data plot due to this.
        """
        nonlocal data, min_indices, max_indices, title

        if column_name == "Magnetic Field (Oe)":
            
            if not len(max_indices) == 1:
                title = "(Esimene min indeks eemaldatud)"
                first_index = min_indices[0]
                first_val = data.loc[first_index, column_name]
                # print(f"{first_index=}")
                # print(f"{first_val=}")
                if -1 < first_val < 1:
                    min_indices = min_indices[1:]
                
    removeSpecialCaseIndex()
    
    # Create a DataFrame to store results
    local_peaks = pd.DataFrame(index=index)
    local_peaks['min'] = np.nan
    local_peaks['max'] = np.nan
    
    # Fill in the 'min' and 'max' columns with peak values 
    local_peaks.loc[min_indices, 'min'] = data.loc[min_indices, column_name]
    local_peaks.loc[max_indices, 'max'] = data.loc[max_indices, column_name]
    
    # Extract max min indices
    mask = local_peaks.notna()
    max_indices = local_peaks["max"].index[mask["max"]]
    min_indices = local_peaks["min"].index[mask["min"]]
    
    # Plot results, tegelikult pole vaja, aga hea kontrollida kas tegi õigesti
    plt.scatter(index, local_peaks['min'], c='r', label='Minima')
    plt.scatter(index, local_peaks['max'], c='g', label='Maxima')
    plt.plot(index, data[column_name], label=column_name)
    
    if column_name == "Temperature (K)":
        unit = "Oe"
    else:
        unit = "K"
        
    plt.title(f"Extrema graph for {const} {unit} \n {title}")
    plt.legend()
    plt.show()
    min_max = [min_indices, max_indices]
    return min_max 


def separateMeasurements(original_dataframe, min_max_index, measurement_indices, column_name): 
    """
    Separates the points based on the separation indices and returns the separated series in pairs.
    
    Separates them based on the expected way: from the first extrema to the second one and then to the 
    third one, so it creates a pair with ascending/descending (not necessarily in this order) part.

    Parameters
    ----------
    min_max_index : LIST OF [pandas.Index,pandas.Index]
        List with the indices for the separation.
    measurement_indices : LIST OF INT
        List with measurement indices.
    column_name : STRING
        Name of the column to use based on the measurement.

    Returns
    -------
    separated_pairs : LIST OF LIST OF DATAFRAME
        All the measurement pairs in dataframe pairs.
    pair_indices : LIST OF LIST OF INT
        All of the indices for the pairs in a nested list.

    """

    separated_pair_all = []
    pair_indices = []
     
    #First assigns the correct indices, assumes data is shaped as + - + or - + -
    if min_max_index[0][0] < min_max_index[1][0]: #This case if for when the data is min->max->min
        min_index_list = min_max_index[0].tolist()
        max_index_list = min_max_index[1].tolist()
    else:                                         #This case is for when the data is max->min->max, it flips the indices for the iteration logic
        min_index_list = min_max_index[1].tolist()
        max_index_list = min_max_index[0].tolist()

    iteration_index = 0

    measurement = original_dataframe[[column_name,"Moment (emu)"]].loc[measurement_indices]

    for max_index in max_index_list: #Slices them from min to max and from max to min pairs
        
        separated_pairs = []
        indices_pair1 = []
        indices_pair2 = []
        
        if max_index in measurement_indices: #Checks if 
            
            sliced1 = measurement.loc[min_index_list[iteration_index]:max_index] #paaride data
            separated_pairs.append(sliced1)
            
            indices_pair1 = original_dataframe.loc[min_index_list[iteration_index]:max_index].index.tolist() #paaride indeksid
            
            if iteration_index == len(min_index_list) - 1:
                
                sliced2 = measurement.loc[max_index+1:min_index_list[iteration_index]]
                
                indices_pair2 = original_dataframe.loc[max_index+1:min_index_list[iteration_index]].index.tolist()
                
            else:
                
                sliced2 = measurement.loc[max_index+1:min_index_list[iteration_index+1]]
                
                indices_pair2 = original_dataframe.loc[max_index+1:min_index_list[iteration_index+1]].index.tolist()
        else:
            max_index_list = max_index_list[iteration_index:]

            break
        
        pair_indices.append(indices_pair1 + indices_pair2)
        separated_pairs.append(sliced2)
        separated_pair_all.append(separated_pairs)
        
        iteration_index += 1
        
    return separated_pair_all, pair_indices

def setPointsColor(original_dataframe, pairs, colors):
    """
    Assigns a color to each pair in the original measurement dataframe.

    Parameters
    ----------
    pairs : LIST OF LIST OF DATAFRAMES
        All the measurement pairs in dataframe pairs.

    Returns
    -------
    None.

    """
    
    global first_indices, second_indices, color_index, all_indices
    
    for pair in pairs:
        all_indices = []
        
        first_indices = pair[0].index.tolist()
        second_indices = pair[1].index.tolist()
        all_indices = first_indices + second_indices
        
        original_dataframe.loc[all_indices, "color"] = colors[color_index]
        
        color_index += 1
    
        if color_index == len(colors): #if the colors are used up it goes back to the beginning
            color_index = 0
            
    return None

def appendPar(x, y ,z):
    lis = [x, y ,z]
    return lis

def addParameterColumns(original_dataframe, separated_pairs, data_type, parameters):
    """
    Adds multiple columns of interest to the SEPARATED_* variable and also adds a unit row with the
    unit of the column.

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

    temp = "Temperature (K)"
    temp_unit = "K"
    
    field = "Magnetic Field (Oe)"
    field_unit = "Oe"
    
    moment = "Moment (emu)"
    moment_unit = "emu"
    error = "M. Std. Err. (emu)"
    
    momentDivMass = "Moment (emu)/mass(g)"
    momentDivMass_unit = "emu/g"
    
    momentDivArea = "Moment (emu)/area(cm2)"
    momentDivArea_unit = "emu/cm2"
    
    momentDivVolume = "Moment (emu)/volume(cm3)"
    momentDivVolume_unit = "emu/cm3"
    
    susceptibility = "Susceptibility (emu/g Oe)"
    susceptibility_unit = "emu/g*Oe"
    
    oneOverSusceptibility = "1/Susceptibility"
    oneOverSusceptibility_unit = "g*Oe/emu"
    
    SAMPLE_MASS_g = parameters[0] if parameters[0] else None
    SAMPLE_AREA_CM2 = parameters[1] if parameters[1] else None
    THICKNESS = parameters[2] if parameters[2] else None
    
    volume = SAMPLE_AREA_CM2*THICKNESS if SAMPLE_AREA_CM2 and THICKNESS else None

    unit_row = None
    
    for i ,pair in enumerate(separated_pairs):
        
        for j, series in enumerate(pair):

            indices = series.index
                
            if data_type == "MvsH":
                
                series[temp] = original_dataframe.loc[indices, temp]
                unit_row = pd.DataFrame({ field: [field_unit], moment: [moment_unit], "True Field (Oe)": [field_unit], temp: [temp_unit],
                                        error: [moment_unit], momentDivMass: [momentDivMass_unit], momentDivArea: [momentDivArea_unit],
                                        momentDivVolume: [momentDivVolume_unit],susceptibility: [susceptibility_unit], oneOverSusceptibility: [oneOverSusceptibility_unit] }, index=['unit'])
                
            elif data_type == "MvsT":
                
                series[field] = original_dataframe.loc[indices, field]
                unit_row = pd.DataFrame({ temp: [temp_unit], moment: [moment_unit], field: [field_unit],
                                        error: [moment_unit], momentDivMass: [momentDivMass_unit], momentDivArea: [momentDivArea_unit],
                                        momentDivVolume: [momentDivVolume_unit],susceptibility: [susceptibility_unit], oneOverSusceptibility: [oneOverSusceptibility_unit] }, index=['unit'])
            
            series[ error] = original_dataframe.loc[indices, error]
            series[momentDivMass] = series[moment]/SAMPLE_MASS_g if SAMPLE_MASS_g else None
            series[ momentDivArea] = series[moment]/SAMPLE_AREA_CM2 if SAMPLE_AREA_CM2 else None
            series[ momentDivVolume] = series[moment]/volume if volume else None
            series[susceptibility] = series[moment]/(SAMPLE_MASS_g*series[field]) if SAMPLE_MASS_g else None
            series[oneOverSusceptibility] = 1/(series[moment]/(SAMPLE_MASS_g*series[field])) if SAMPLE_MASS_g else None
            
            # Concatenate the new row DataFrame and the original DataFrame
            pair[j] = pd.concat([unit_row, series])
            
        separated_pairs[i] = pair
        
    return None