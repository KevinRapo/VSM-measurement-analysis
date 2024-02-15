# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 11:25:34 2024

@author: Kevin
"""
from modules import read_in as read
from modules import prep
from modules import plot
from modules import save

from modules.prep import setColor
from modules.prep import MvsH
from modules.prep import MeasurementObj

import traceback
import copy

# -------------- OPENING THE FILE AND INDEXING IT -------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------

# Ask user input to get a path to datafile(using Measurement1 abbreviation)
M1 = MeasurementObj()

#variables from the object
FILE_PATH, USER_PATH = M1.file_path, M1.user_path 
HEADER, ORIGINAL_DATAFRAME = M1.header, M1.df
OPTION_TYPE = M1.option_type
ORIGINAL_DATAFRAME = M1.df
SAMPLE_MASS_g = M1.sample_mass_g
SAMPLE_AREA_CM2 = M1.sample_area_cm2
TEMPERATURES_OF_INTEREST, MAGNETIC_FIELDS_OF_INTEREST = M1.temperatures_of_interest, M1.magnetic_fields_of_interest

# siin peaks olema try ja catch exepction ümber
THICKNESS = M1.thickness

# Color list for color idx and initializing the starting color idx with just black
COLORS = M1.colors
folder_path = M1.folder_path

# --------------------------MvsT cycle------------------------------------------------------
if MAGNETIC_FIELDS_OF_INTEREST.size <= 0:
    print('no MvsT detected')
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    print('--------<<<<<<<<<>>>>>>>>>>-----------')

else:
    print(' MvsT data detected')
    print(MAGNETIC_FIELDS_OF_INTEREST)

    def allUniqueConstMeasurementsMvsT(const):

        global unfiltered_MvsT_indices, MvsT_INDICES, separation_index_MvsT, SEPARATED_MvsT, MvsT_pair_indices, \
            test1

        # unfiltered_MvsT_indices = prep.getMeasurementMvsT(ORIGINAL_DATAFRAME, const)
        MvsT_INDICES = prep.getMeasurementMvsT(ORIGINAL_DATAFRAME, const)
        # MvsT_INDICES = prep.filterMeasurementIndices(unfiltered_MvsT_indices)

        separation_index_MvsT = prep.separationIndexForSingleSeries(ORIGINAL_DATAFRAME, MvsT_INDICES,
                                                                    "Temperature (K)", const)
        try:
            SEPARATED_MvsT, MvsT_pair_indices = prep.separateMeasurements(ORIGINAL_DATAFRAME, separation_index_MvsT,
                                                                          MvsT_INDICES, "Temperature (K)")
        except IndexError:
            print("\nChanged separateMeasurements parameter x = 0.5, was 0.1\n")

            separation_index_MvsT = prep.separationIndexForSingleSeries(ORIGINAL_DATAFRAME, MvsT_INDICES,
                                                                        "Temperature (K)", const, x=0.5)  # the indices where the separation is going to be done
            SEPARATED_MvsT, MvsT_pair_indices = prep.separateMeasurements(ORIGINAL_DATAFRAME, separation_index_MvsT,
                                                                          MvsT_INDICES, "Temperature (K)")

        setColor.Points(ORIGINAL_DATAFRAME, SEPARATED_MvsT, COLORS)
        # prep.setPointsColor(ORIGINAL_DATAFRAME, SEPARATED_MvsT, COLORS)

        plot.plotMvsT(SEPARATED_MvsT, const, ORIGINAL_DATAFRAME, folder_path)

        ORIGINAL_DATAFRAME.loc[MvsT_INDICES, "Type"] = "MvsT"

        sample_parameters = prep.appendPar(
            SAMPLE_MASS_g, SAMPLE_AREA_CM2, THICKNESS)
        prep.addParameterColumns(
            ORIGINAL_DATAFRAME, SEPARATED_MvsT, "MvsT", sample_parameters)
        save.appendAndSave(SEPARATED_MvsT, "MvsT", const, folder_path)
        return None

    for const in MAGNETIC_FIELDS_OF_INTEREST:
        try:
            # allUniqueConstMeasurementsMvsT("const") #UNCOMMENTI SEE KUI TAHAD NÄHA KUIDAS ERRORI KORRAL KÄITUB, SUVALINE ARGUMENT SELLEL MIS ERRORI VISKAB LIHTSALT
            allUniqueConstMeasurementsMvsT(const)  # ÕIGE MILLEGA TÖÖTAB

        except:
            # mingi indikaator näiteks timeseries et need punktid feilisid
            print("__________________________WARNING_____________________________")
            print(
                f"-----------------RUN ON {const} OE FAILED--------------------\n")
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

        global unfiltered_MvsH_indices, MvsH_INDICES, separation_index_MvsH, SEPARATED_MvsH, MvsH_pair_indices, correction_field_value, \
            CORRECTION_TABLES, test2

        # unfiltered_MvsH_indices = prep.getMeasurementMvsH(ORIGINAL_DATAFRAME, const)
        MvsH_INDICES = MvsH.getMeasurementMvsH(ORIGINAL_DATAFRAME, const)
        # if len(unfiltered_MvsH_indices) == 0:#!!! see check tuleb mujale panna kui need kokku panna
        #     #print("*********************")
        #     print(f"\nFalse positive for MvsH at {const} K\nNo actual measurement at that temperature")
        #     #print("*********************")
        #     return None

        # MvsH_INDICES = prep.filterMeasurementIndices(unfiltered_MvsH_indices)

        separation_index_MvsH = prep.separationIndexForSingleSeries(ORIGINAL_DATAFRAME, MvsH_INDICES,
                                                                    "Magnetic Field (Oe)", const)

        try:
            SEPARATED_MvsH, MvsH_pair_indices = prep.separateMeasurements(ORIGINAL_DATAFRAME, separation_index_MvsH,
                                                                          MvsH_INDICES, "Magnetic Field (Oe)")
        except IndexError:
            print("\nChanged separateMeasurements parameter x = 0.5, was 0.1\n")

            separation_index_MvsH = prep.separationIndexForSingleSeries(ORIGINAL_DATAFRAME, MvsH_INDICES,
                                                                        "Magnetic Field (Oe)", const, x=0.5)  # the indices where the separation is going to be done
            SEPARATED_MvsH, MvsH_pair_indices = prep.separateMeasurements(ORIGINAL_DATAFRAME, separation_index_MvsH,
                                                                          MvsH_INDICES, "Magnetic Field (Oe)")

        # ??? vist oli mingi error aga 1_CoFe2O4_700degC_Hys_at300K_2TSweep_19062023 faili puhul vaja, /MvsH mitu samal
        # SEPARATED_MvsH = prep.removeBleedingElement(SEPARATED_MvsH)

        correction_field_value = MvsH.roundFieldForCorrection(SEPARATED_MvsH)
        CORRECTION_TABLES = MvsH.CorrectionTableToDict(
            correction_field_value, USER_PATH)
        MvsH.interpolateMvsH(SEPARATED_MvsH, CORRECTION_TABLES)

        setColor.Points(ORIGINAL_DATAFRAME, SEPARATED_MvsH, COLORS)
        # prep.setPointsColor(ORIGINAL_DATAFRAME, SEPARATED_MvsH, COLORS)

        plot.plotMvsH(SEPARATED_MvsH, const, ORIGINAL_DATAFRAME, folder_path)

        ORIGINAL_DATAFRAME.loc[MvsH_INDICES, "Type"] = "MvsH"

        sample_parameters = prep.appendPar(
            SAMPLE_MASS_g, SAMPLE_AREA_CM2, THICKNESS)
        prep.addParameterColumns(
            ORIGINAL_DATAFRAME, SEPARATED_MvsH, "MvsH", sample_parameters)
        save.appendAndSave(SEPARATED_MvsH, "MvsH", const, folder_path)

        return None

    for const in TEMPERATURES_OF_INTEREST:
        try:
            allUniqueConstMeasurementsMvsH(const)  # ÕIGE MILLEGA TÖÖTAB

        except:
            # mingi indikaator näiteks timeseries et need punktid feilisid
            print("__________________________WARNING_____________________________")
            print(
                f"-----------------RUN ON {const} K FAILED--------------------\n")
            print(traceback.format_exc())
            # print("______________________________________________________________\n")
            pass
    print('--------<<<<<<<<<>>>>>>>>>>-----------')
    print('--------<<<<<<<<<>>>>>>>>>>-----------')

if MAGNETIC_FIELDS_OF_INTEREST.size <= 0 and TEMPERATURES_OF_INTEREST.size <= 0:
    print('Error, ei suutnud eraldada MvsH ja MvsT mõõtmisi')

# Plots temp, field and moment against time
plot.plotMeasurementTimeseries(ORIGINAL_DATAFRAME, folder_path)
