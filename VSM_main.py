# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 11:25:34 2024

@author: Kevin
"""
from modules import read_in as R
from modules import prep as P
from modules import plot as plot
from modules import save as S

import traceback
import copy

#-------------- OPENING THE FILE AND INDEXING IT -------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------

# Ask user input to get a path to datafile
FILE_PATH, USER_PATH = R.FilePathAndcwd()

# Read the datafile
HEADER, ORIGINAL_DATAFRAME = R.readDatafile(FILE_PATH)
ORIGINAL_DATAFRAME = ORIGINAL_DATAFRAME
ORIGINAL_COPY = copy.deepcopy(ORIGINAL_DATAFRAME)
# VSM or ACMSII? or maybe HC or ETO in the future
OPTION_TYPE = R.DatafileType(HEADER)
#print(OPTION_TYPE) kas teha nii et funk ise ei prindi ja prindid kui tahad või funktsioon prindib anyway?

ORIGINAL_DATAFRAME = R.ParseDf(OPTION_TYPE, ORIGINAL_DATAFRAME)

#parse HEADER
SAMPLE_MASS_g = R.getMassInGrams(HEADER)
SAMPLE_AREA_CM2 = R.getAreaCM2(HEADER)
#siin peaks olema try ja catch exepction ümber
THICKNESS = R.getThickness(HEADER)

#Color list for color idx and initializing the starting color idx with just black
COLORS = ["red", "green", "blue", "yellow", "brown", "purple", "orange", "pink", "olive", "magenta"]
ORIGINAL_DATAFRAME["color"] = "black"

print("_________chechMeasurementType2-----------")
# Tagastab kaks Pandas.Seriest: temperatures_of_interest, magnetic_fields_of_interest
TEMPERATURES_OF_INTEREST, MAGNETIC_FIELDS_OF_INTEREST= P.checkMeasurementType2(ORIGINAL_DATAFRAME)
print("_________end-----------\n")

#MAGNETIC_FIELDS_OF_INTEREST = list(MAGNETIC_FIELDS_OF_INTEREST)

print('--------<<<<<<<<<>>>>>>>>>>-----------')
print('--------<<<<<<<<<>>>>>>>>>>-----------')

#creates a column "Type" for each data point type
ORIGINAL_DATAFRAME["Type"] = ""

#Creates a folder for the current data file to save related files
folder_path = S.MakeSaveFolder(FILE_PATH)

# MvsT cycle
if MAGNETIC_FIELDS_OF_INTEREST.size <= 0:
    print('no MvsT detected')
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    
else:
    print(' MvsT data detected')
    print(MAGNETIC_FIELDS_OF_INTEREST)

    #test1 = []
    
    def allUniqueConstMeasurementsMvsT(const):
        
        global unfiltered_MvsT_indices, MvsT_INDICES, separation_index_MvsT, SEPARATED_MvsT, MvsT_pair_indices,\
            test1
        
        unfiltered_MvsT_indices = P.getMeasurementMvsT(ORIGINAL_DATAFRAME, const)
        MvsT_INDICES = P.filterMeasurementIndices(unfiltered_MvsT_indices)
        
        separation_index_MvsT = P.separationIndexForSingleSeries(ORIGINAL_DATAFRAME, MvsT_INDICES,
                                                                 "Temperature (K)", const)
        try:
            SEPARATED_MvsT, MvsT_pair_indices = P.separateMeasurements(ORIGINAL_DATAFRAME, separation_index_MvsT,
                                                                       MvsT_INDICES, "Temperature (K)")
        except IndexError:
            print("\nChanged separateMeasurements parameter x = 0.5, was 0.1\n")
            
            separation_index_MvsT = P.separationIndexForSingleSeries(ORIGINAL_DATAFRAME, MvsT_INDICES,
                                                                     "Temperature (K)", const, x=0.5)# the indices where the separation is going to be done
            SEPARATED_MvsT, MvsT_pair_indices = P.separateMeasurements(ORIGINAL_DATAFRAME, separation_index_MvsT,
                                                                       MvsT_INDICES, "Temperature (K)")
        
        P.setPointsColor(ORIGINAL_DATAFRAME, SEPARATED_MvsT, COLORS)
        
        plot.plotMvsT(SEPARATED_MvsT, const, ORIGINAL_DATAFRAME, folder_path)
        
        ORIGINAL_DATAFRAME.loc[MvsT_INDICES, "Type"] = "MvsT"
        
        sample_parameters = P.appendPar(SAMPLE_MASS_g, SAMPLE_AREA_CM2, THICKNESS)
        P.addParameterColumns(ORIGINAL_DATAFRAME, SEPARATED_MvsT, "MvsT", sample_parameters)
        S.appendAndSave(SEPARATED_MvsT, "MvsT", const, folder_path)
        return None

    #For cycling the colors on MvsT run
    color_index = 0
    for const in MAGNETIC_FIELDS_OF_INTEREST:
        try:
            #allUniqueConstMeasurementsMvsT("const") #UNCOMMENTI SEE KUI TAHAD NÄHA KUIDAS ERRORI KORRAL KÄITUB, SUVALINE ARGUMENT SELLEL MIS ERRORI VISKAB LIHTSALT
            allUniqueConstMeasurementsMvsT(const) #ÕIGE MILLEGA TÖÖTAB
        except:
            #mingi indikaator näiteks timeseries et need punktid feilisid
            print("__________________________WARNING_____________________________")
            print(f"-----------------RUN ON {const} OE FAILED--------------------\n")
            print(traceback.format_exc())
            print("______________________________________________________________\n")
            pass      
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    
# MvsH cycle
if TEMPERATURES_OF_INTEREST.size <= 0:
    print('no MvsH detected')
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    
else:
    print(' MvsH data detected')
    print(TEMPERATURES_OF_INTEREST)

    #test2 = []
    
    def allUniqueConstMeasurementsMvsH(const):
        
        global unfiltered_MvsH_indices, MvsH_INDICES, separation_index_MvsH, SEPARATED_MvsH, MvsH_pair_indices, correction_field_value,\
            CORRECTION_TABLES, test2
        
        unfiltered_MvsH_indices = P.getMeasurementMvsH(ORIGINAL_DATAFRAME, const)
        
        if len(unfiltered_MvsH_indices) == 0:
            #print("*********************")
            print(f"\nFalse positive for MvsH at {const} K\nNo actual measurement at that temperature")
            #print("*********************")
            return None
        
        MvsH_INDICES = P.filterMeasurementIndices(unfiltered_MvsH_indices)
        separation_index_MvsH = P.separationIndexForSingleSeries(ORIGINAL_DATAFRAME, MvsH_INDICES,
                                                                 "Magnetic Field (Oe)", const)
        
        try:
            SEPARATED_MvsH, MvsH_pair_indices = P.separateMeasurements(ORIGINAL_DATAFRAME, separation_index_MvsH,
                                                                       MvsH_INDICES, "Magnetic Field (Oe)")
        except IndexError:
            print("\nChanged separateMeasurements parameter x = 0.5, was 0.1\n")
            
            separation_index_MvsH = P.separationIndexForSingleSeries(ORIGINAL_DATAFRAME, MvsH_INDICES,
                                                                     "Magnetic Field (Oe)", const, x=0.5)# the indices where the separation is going to be done
            SEPARATED_MvsH, MvsH_pair_indices = P.separateMeasurements(ORIGINAL_DATAFRAME, separation_index_MvsH,
                                                                       MvsH_INDICES, "Magnetic Field (Oe)")
            
        #???
        #SEPARATED_MvsH = removeBleedingElement(SEPARATED_MvsH)
        
        correction_field_value = P.roundFieldForCorrection(SEPARATED_MvsH)
        CORRECTION_TABLES = P.CorrectionTableToDict(correction_field_value, USER_PATH)
        P.interpolateMvsH(SEPARATED_MvsH, CORRECTION_TABLES)
        
        P.setPointsColor(ORIGINAL_DATAFRAME, SEPARATED_MvsH, COLORS)
        
        plot.plotMvsH(SEPARATED_MvsH, const, ORIGINAL_DATAFRAME, folder_path)
        
        ORIGINAL_DATAFRAME.loc[MvsH_INDICES, "Type"] = "MvsH"
        
        sample_parameters = P.appendPar(SAMPLE_MASS_g, SAMPLE_AREA_CM2, THICKNESS)
        P.addParameterColumns(ORIGINAL_DATAFRAME, SEPARATED_MvsH, "MvsH", sample_parameters)
        S.appendAndSave(SEPARATED_MvsH, "MvsH", const, folder_path)
        
        return None
    
    # For cycling the colors on the MvsH run
    color_index = 0
    for const in TEMPERATURES_OF_INTEREST:
        try:
            #allUniqueConstMeasurementsMvsH("const") #UNCOMMENTI SEE KUI TAHAD NÄHA KUIDAS ERRORI KORRAL KÄITUB, SUVALINE ARGUMENT SELLEL MIS ERRORI VISKAB LIHTSALT
            allUniqueConstMeasurementsMvsH(const) #ÕIGE MILLEGA TÖÖTAB
            
        except:
            #mingi indikaator näiteks timeseries et need punktid feilisid
            print("__________________________WARNING_____________________________")
            print(f"-----------------RUN ON {const} K FAILED--------------------\n")
            print(traceback.format_exc())
            #print("______________________________________________________________\n")
            pass
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    
if MAGNETIC_FIELDS_OF_INTEREST.size <= 0 and TEMPERATURES_OF_INTEREST.size <= 0:
    print('Error, ei suutnud eraldada MvsH ja MvsT mõõtmisi')

#Plots temp, field and moment against time
plot.plotMeasurementTimeseries(ORIGINAL_DATAFRAME, folder_path)