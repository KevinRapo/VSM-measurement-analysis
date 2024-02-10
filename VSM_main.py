# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 11:25:34 2024

@author: Kevin
"""
from modules import read_in as read
from modules import prep
from modules import plot
from modules import save

import traceback
import copy

#-------------- OPENING THE FILE AND INDEXING IT -------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------

# Ask user input to get a path to datafile
FILE_PATH, USER_PATH = read.FilePathAndcwd()

# Read the datafile
HEADER, ORIGINAL_DATAFRAME = read.readDatafile(FILE_PATH)
ORIGINAL_DATAFRAME = ORIGINAL_DATAFRAME
ORIGINAL_COPY = copy.deepcopy(ORIGINAL_DATAFRAME)
# VSM or ACMSII? or maybe HC or ETO in the future
OPTION_TYPE = read.DatafileType(HEADER)
#print(OPTION_TYPE) kas teha nii et funk ise ei prindi ja prindid kui tahad või funktsioon prindib anyway?

ORIGINAL_DATAFRAME = read.ParseDf(OPTION_TYPE, ORIGINAL_DATAFRAME)

#parse HEADER
SAMPLE_MASS_g = read.getMassInGrams(HEADER)
SAMPLE_AREA_CM2 = read.getAreaCM2(HEADER)
#siin peaks olema try ja catch exepction ümber
THICKNESS = read.getThickness(HEADER)

#Color list for color idx and initializing the starting color idx with just black
COLORS = ["red", "green", "blue", "yellow", "brown", "purple", "orange", "pink", "olive", "magenta"]
ORIGINAL_DATAFRAME["color"] = "black"

print("_________chechMeasurementType2-----------")
# Tagastab kaks Pandas.Seriest: temperatures_of_interest, magnetic_fields_of_interest
TEMPERATURES_OF_INTEREST, MAGNETIC_FIELDS_OF_INTEREST= prep.checkMeasurementType2(ORIGINAL_DATAFRAME)
print("_________end-----------\n")

#MAGNETIC_FIELDS_OF_INTEREST = list(MAGNETIC_FIELDS_OF_INTEREST)

print('--------<<<<<<<<<>>>>>>>>>>-----------')
print('--------<<<<<<<<<>>>>>>>>>>-----------')

#creates a column "Type" for each data point type
ORIGINAL_DATAFRAME["Type"] = ""

#Creates a folder for the current data file to save related files
folder_path = save.MakeSaveFolder(FILE_PATH)

# --------------------------MvsT cycle------------------------------------------------------
if MAGNETIC_FIELDS_OF_INTEREST.size <= 0:
    print('no MvsT detected')
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    
else:
    print(' MvsT data detected')
    print(MAGNETIC_FIELDS_OF_INTEREST)
    
    
    def allUniqueConstMeasurementsMvsT(const):
        
        global unfiltered_MvsT_indices, MvsT_INDICES, separation_index_MvsT, SEPARATED_MvsT, MvsT_pair_indices,\
            test1
        
        unfiltered_MvsT_indices = prep.getMeasurementMvsT(ORIGINAL_DATAFRAME, const)
        MvsT_INDICES = prep.filterMeasurementIndices(unfiltered_MvsT_indices)
        
        separation_index_MvsT = prep.separationIndexForSingleSeries(ORIGINAL_DATAFRAME, MvsT_INDICES,
                                                                 "Temperature (K)", const)
        try:
            SEPARATED_MvsT, MvsT_pair_indices = prep.separateMeasurements(ORIGINAL_DATAFRAME, separation_index_MvsT,
                                                                       MvsT_INDICES, "Temperature (K)")
        except IndexError:
            print("\nChanged separateMeasurements parameter x = 0.5, was 0.1\n")
            
            separation_index_MvsT = prep.separationIndexForSingleSeries(ORIGINAL_DATAFRAME, MvsT_INDICES,
                                                                     "Temperature (K)", const, x=0.5)# the indices where the separation is going to be done
            SEPARATED_MvsT, MvsT_pair_indices = prep.separateMeasurements(ORIGINAL_DATAFRAME, separation_index_MvsT,
                                                                       MvsT_INDICES, "Temperature (K)")
        
        prep.setColor.Points(ORIGINAL_DATAFRAME, SEPARATED_MvsT, COLORS)
        #prep.setPointsColor(ORIGINAL_DATAFRAME, SEPARATED_MvsT, COLORS)
        
        plot.plotMvsT(SEPARATED_MvsT, const, ORIGINAL_DATAFRAME, folder_path)
        
        ORIGINAL_DATAFRAME.loc[MvsT_INDICES, "Type"] = "MvsT"
        
        sample_parameters = prep.appendPar(SAMPLE_MASS_g, SAMPLE_AREA_CM2, THICKNESS)
        prep.addParameterColumns(ORIGINAL_DATAFRAME, SEPARATED_MvsT, "MvsT", sample_parameters)
        save.appendAndSave(SEPARATED_MvsT, "MvsT", const, folder_path)
        return None


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
    
# ---------------------MvsH cycle---------------------------------------------------------------
if TEMPERATURES_OF_INTEREST.size <= 0:
    print('no MvsH detected')
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    
else:
    print(' MvsH data detected')
    print(TEMPERATURES_OF_INTEREST)
    
    
    def allUniqueConstMeasurementsMvsH(const):
        
        global unfiltered_MvsH_indices, MvsH_INDICES, separation_index_MvsH, SEPARATED_MvsH, MvsH_pair_indices, correction_field_value,\
            CORRECTION_TABLES, test2
        
        unfiltered_MvsH_indices = prep.getMeasurementMvsH(ORIGINAL_DATAFRAME, const)
        
        if len(unfiltered_MvsH_indices) == 0:
            #print("*********************")
            print(f"\nFalse positive for MvsH at {const} K\nNo actual measurement at that temperature")
            #print("*********************")
            return None
        
        MvsH_INDICES = prep.filterMeasurementIndices(unfiltered_MvsH_indices)
        separation_index_MvsH = prep.separationIndexForSingleSeries(ORIGINAL_DATAFRAME, MvsH_INDICES,
                                                                 "Magnetic Field (Oe)", const)
        
        try:
            SEPARATED_MvsH, MvsH_pair_indices = prep.separateMeasurements(ORIGINAL_DATAFRAME, separation_index_MvsH,
                                                                       MvsH_INDICES, "Magnetic Field (Oe)")
        except IndexError:
            print("\nChanged separateMeasurements parameter x = 0.5, was 0.1\n")
            
            separation_index_MvsH = prep.separationIndexForSingleSeries(ORIGINAL_DATAFRAME, MvsH_INDICES,
                                                                     "Magnetic Field (Oe)", const, x=0.5)# the indices where the separation is going to be done
            SEPARATED_MvsH, MvsH_pair_indices = prep.separateMeasurements(ORIGINAL_DATAFRAME, separation_index_MvsH,
                                                                       MvsH_INDICES, "Magnetic Field (Oe)")
            
        #???
        #SEPARATED_MvsH = removeBleedingElement(SEPARATED_MvsH)
        
        correction_field_value = prep.roundFieldForCorrection(SEPARATED_MvsH)
        CORRECTION_TABLES = prep.CorrectionTableToDict(correction_field_value, USER_PATH)
        prep.interpolateMvsH(SEPARATED_MvsH, CORRECTION_TABLES)
        
        prep.setColor.Points(ORIGINAL_DATAFRAME, SEPARATED_MvsH, COLORS)
        #prep.setPointsColor(ORIGINAL_DATAFRAME, SEPARATED_MvsH, COLORS)
        
        plot.plotMvsH(SEPARATED_MvsH, const, ORIGINAL_DATAFRAME, folder_path)
        
        ORIGINAL_DATAFRAME.loc[MvsH_INDICES, "Type"] = "MvsH"
        
        sample_parameters = prep.appendPar(SAMPLE_MASS_g, SAMPLE_AREA_CM2, THICKNESS)
        prep.addParameterColumns(ORIGINAL_DATAFRAME, SEPARATED_MvsH, "MvsH", sample_parameters)
        save.appendAndSave(SEPARATED_MvsH, "MvsH", const, folder_path)
        
        return None
    
    for const in TEMPERATURES_OF_INTEREST:
        try:
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