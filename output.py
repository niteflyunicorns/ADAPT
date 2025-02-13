#########################################################################################
### Program: ADAPT (Anomaly Detection for Asteroid Patterns and Trends)
### Programmer: Savannah Chappus
### Last Update: 1.31.2025
###
### File: output.py
### Use: exports or prints program results
#########################################################################################

### IMPORTS #############################################################################
from tabulate import tabulate
import numpy as np
import pandas as pd

### VARIABLES ###########################################################################
useMsg = "python ADAPT.py maxIn offset fltrType fltrLvl plots exportFlg fileType fileName astName featFltr lB uB \n\n\
See the README.md for more information."


#########################################################################################
### Function: exportFile
### Inputs: file type (number 1, 2, 3), file name, data to export
### Returns: none
#########################################################################################
def exportFile( fileType, filename, data ):
    print( "Exporting data...\n" )
    if fileType == 1:
        data.to_html( buf=filename, index=False )
    if fileType == 2:
        data.to_csv( filename, index=False )
    if fileType == 3: # normal text file
        with open( filename + ".txt", 'w' ) as f:
            f.write( tabulate( data, headers='keys', tablefmt='simple_outline' ) )
            f.write( "\n" )


#########################################################################################
### Function: help
### Inputs: none
### Returns: none (prints help message on screen)
#########################################################################################
def help( ):
    print( useMsg )


#########################################################################################
### Function: screenDisplay
### Inputs: data, title header
### Returns: none (prints help message on screen)
#########################################################################################
def screenDisplay( data, header ):
    print( "\n\n" )
    print( header + ( '-' * 50 ) )
    tabulate( data, headers='keys', tablefmt='simple_outline' )
    print( "\n" )


#########################################################################################
### Function: formatDataTable
### Inputs: sigma matrix, antares IDs array, asteroid name array,
###          number of asteroids, and number of features
### Returns: nicely formatted table for display
#########################################################################################
#@profile
def formatDataTable( sigmaMatrix, antIDS, nameArray, maxIn, numFeatures ):
    listNames = [ ]
    idArray = [ ]
    listNames= np.array( antIDS )
    idArray = np.reshape( listNames, ( maxIn, numFeatures ) )
    if maxIn != 1:
        dataset = pd.DataFrame(
            { 'Name': nameArray,
             'elong': sigmaMatrix[ :, 0 ],
             'ZTF-ELONG': idArray[ :, 0 ],
             'rb': sigmaMatrix[ :, 1 ],
             'ZTF-RB': idArray[ :, 1 ],
             'H': sigmaMatrix[ :, 2 ],
             'ZTF-H': idArray[ :, 2 ],
             'mag18omag8': sigmaMatrix[ :, 3 ],
             'ZTF-MAG18OMAG8': idArray[ :, 3 ],
             'Row Sum': sigmaMatrix[ :, 4 ],
             'Abs Row Sum': sigmaMatrix[ :, 5 ],
             'Rating': sigmaMatrix[ :, 6 ]
            } )
    if maxIn == 1:
        ### ERROR: code below only works with 1 asteroid from "view one"
        ### not from 'run program' due to formatting. TODO: Fix this
        dataset = pd.DataFrame(
            { 'Name': nameArray,
             'elong': sigmaMatrix[ 0 ],
             'ZTF-ELONG': idArray[ :, 0 ],
             'rb': sigmaMatrix[ 1 ],
             'ZTF-RB': idArray[ :, 1 ],
             'H': sigmaMatrix[ 2 ],
             'ZTF-H': idArray[ :, 2 ],
             'mag18omag8': sigmaMatrix[ 3 ],
             'ZTF-MAG18OMAG8': idArray[ :, 3 ],
             'Row Sum': sigmaMatrix[ 4 ],
             'Abs Row Sum': sigmaMatrix[ 5 ],
             'Rating': sigmaMatrix[ 6 ]
            } )
        
    return dataset
