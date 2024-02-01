# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 11:25:34 2024

@author: Kevin
"""
from modules.read.read_in import *
from modules.prep import prep as P
from modules.plot import plot as plot
from modules.save import save as save
from modules import global_variables  as G

# USER_PATH = os.getcwd()

#-------------- OPENING THE FILE AND INDEXING IT -------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------

# Ask user input to get a path to datafile
FilePathAndcwd()

# Read the datafile
HEADER, G.ORIGINAL_DATAFRAME = readDatafile(G.FILE_PATH)
ORIGINAL_DATAFRAME = G.ORIGINAL_DATAFRAME
ORIGINAL_COPY = copy.deepcopy(G.ORIGINAL_DATAFRAME)
# VSM or ACMSII? or maybe HC or ETO in the future
OPTION_TYPE = determineDatafileType(HEADER)
#print(OPTION_TYPE) kas teha nii et funk ise ei prindi ja prindid kui tahad või funktsioon prindib anyway?


#Selle lisasin juurde kuna moment tulbas võib olla nan values ja enne pead kõik õiged tulbad võtma, et need eraldada, muidu eemaldab kõik read,
# sest igas reas on mingi tulp nan value'ga
if OPTION_TYPE == "VSM":
    ORIGINAL_DATAFRAME = ORIGINAL_DATAFRAME[["Time Stamp (sec)", "Temperature (K)", "Magnetic Field (Oe)", "Moment (emu)", "M. Std. Err. (emu)"]].dropna()
    ORIGINAL_DATAFRAME = ORIGINAL_DATAFRAME.reset_index(drop = True)
    
elif OPTION_TYPE == "ACMS": #!!! siia veel eraldi check et kas AC või DC
    ORIGINAL_DATAFRAME = ORIGINAL_DATAFRAME[["Time Stamp (sec)", "Temperature (K)", "Magnetic Field (Oe)", "DC Moment (emu)", "DC Std. Err. (emu)"]].dropna()
    ORIGINAL_DATAFRAME = ORIGINAL_DATAFRAME.rename(columns={"DC Moment (emu)": "Moment (emu)", "DC Std. Err. (emu)": "M. Std. Err. (emu)"})
    ORIGINAL_DATAFRAME = ORIGINAL_DATAFRAME.reset_index(drop = True)

#parse HEADER
SAMPLE_MASS_g = getMassInGrams(HEADER)
SAMPLE_AREA_CM2 = getAreaCM2(HEADER)
#siin peaks olema try ja catch exepction ümber
THICKNESS = getThickness(HEADER)


#Color list for color idx and initializing the starting color idx with just black
COLORS = ["red", "green", "blue", "yellow", "brown", "purple", "orange", "pink", "olive", "magenta"]
ORIGINAL_DATAFRAME["color"] = "black"

print("_________chechMeasurementType2-----------")
# Tagastab kaks Pandas.Seriest: temperatures_of_interest, magnetic_fields_of_interest
TEMPERATURES_OF_INTEREST, MAGNETIC_FIELDS_OF_INTEREST= P.checkMeasurementType2(ORIGINAL_DATAFRAME)
print("_________end-----------\n")


print('--------<<<<<<<<<>>>>>>>>>>-----------')
print('--------<<<<<<<<<>>>>>>>>>>-----------')

#creates a column "Type" for each data point type
ORIGINAL_DATAFRAME["Type"] = ""

#Creates a folder for the current data file to save related files
folder_name = os.path.splitext(G.FILE_PATH)[0] + ""
os.makedirs(folder_name, exist_ok = True)

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
        
        unfiltered_MvsT_indices = P.getMeasurementMvsT(const)
        MvsT_INDICES = P.filterMeasurementIndices(unfiltered_MvsT_indices)
        separation_index_MvsT = P.separationIndexForSingleSeries(MvsT_INDICES, "Temperature (K)")
        
        try:
            SEPARATED_MvsT, MvsT_pair_indices = P.separateMeasurements(separation_index_MvsT, MvsT_INDICES, "Temperature (K)")
            
        except IndexError:
            print("\nChanged separateMeasurements parameter x = 0.5, was 0.1\n")
            
            separation_index_MvsT = P.separationIndexForSingleSeries(MvsT_INDICES, "Temperature (K)", x=0.5)# the indices where the separation is going to be done
            SEPARATED_MvsT, MvsT_pair_indices = P.separateMeasurements(separation_index_MvsT, MvsT_INDICES, "Temperature (K)")
        
        P.setPointsColor(SEPARATED_MvsT)
        
        P.plotMvsT(SEPARATED_MvsT, const)
        
        ORIGINAL_DATAFRAME.loc[MvsT_INDICES, "Type"] = "MvsT"
        P.addParameterColumns(SEPARATED_MvsT, "MvsT")
        save.appendAndSave(SEPARATED_MvsT, "MvsT")
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