#########################################################################################
### Program: ADAPT
### Programmer: Savannah Chappus
### Last Update: 1.31.2025
#########################################################################################

## IMPORTS ##############################################################################
from pymongo import MongoClient
from pprint import pprint
import pandas as pd
import statistics as stat
import matplotlib.pyplot as plt
from matplotlib import gridspec
import mplcursors
import numpy as np
import random as rand
import pdb
import sys
import configparser as cfp
#from line_profiler import profile
# custom py file imports
# import asteroidMenuClass as menu

## New Imports ##########################################################################
from AstDataClass import AstData
import plotting as plot # may not need this eventually
import output as out
import getObservations as getObs # may not need this eventually
import viewOneAst as oneAst
import viewMultAst as multAst
import anomRatingADAPT as anomaly
import dbscanADAPT as dbscan
import isoforestADAPT as forest

## GLOBAL VARS ##########################################################################
offset = 0 # for shifting data scope
attrList = "ssnamenr, jd, fid, pid, diffmaglim, ra, dec, magpsf, sigmapsf, \
chipsf, magap, sigmagap, magapbig, sigmagapbig, distnr, magnr, fwhm, elong, rb, \
ssdistnr, ssmagnr, id, night, phaseangle, obsdist, heliodist, H, ltc, mag18omag8"
# attrList is for users to choose attrs to filter by
fltrTypeMsg = \
    "1. 'anomaly' : use the custom sigma-based anomaly rating system (see the README.md for more information). \n\
2. 'dbscan' : use DBSCAN filtering \n\
3. 'isoforest' : use Isolation Forest filtering \n\
4. 'knn' : use K-Nearest Neighbors filtering \n\ "


# Top 4 Attributes of Interest:
# mag180mag8 : sigma value for difference in 18" aperture vs 8" aperture photos
# elong: elong val > 1 means oblong object, if this changes it's interesting
# rb (real-bogus ): value to represent the "validity" or "trustworthiness" of the
# collected data
# H: another measurement of brightness
wantedAttrs = [ "elong", "rb", "H", "mag18omag8" ] # attributes we want to look at
# wantedAttrs = [ ]
dataCols = wantedAttrs.copy()
dataCols.extend( [ 'jd', 'id', 'ssnamenr' ] ) # additional cols needed for processing
numFeatures = len( wantedAttrs )
antIDS = list( ) # list for associated ztf id for observation
weightDict = {
    "H": 1,
    "mag18omag8": 1,
    "elong": 1,
    "rb": 1
} # not currently used 

## FUNCTION DEFINITIONS #################################################################

# clear: takes numerical input and prints that many new lines
# used for clearing the screen to help with readability
def clear( size ):
    print( "\n" * size )

# getInputs: takes an input array and output array. Loops through
# input prompts and gets user input and stores in output array
def getInputs( inArray, outArray ):
    for prompt in inArray:
        value = input( prompt )
        outArray.append( value )


# leave: takes no inputs, prints exit message & ends program
def leave( ):
    print( "Thank you for using SNAPS!\n" )


# this function has been commented out because there is a potential error
# later in the code that may require this to be reintroduced in some form
# # function for stripping data of all 0 entries
# def stripZeros(data, fltrLvl ):
#     #print(data.count(0.0 ) )
#     if int(data.count(0.0 ) ) >= fltrLvl:
#         return [ ]
#     return data

# getFilter: takes no inputs, gets filter type and level input from user
# def getFilter( ):
    # typeDict = { 0: 'Select Filter Type:',
    #             1: 'By number of outlier occurences per night',
    #             2: 'By overall asteroid anomaly rating',
    #             3: 'By weighted attribute filtering',
    #             4: 'None' }
    # menu.display( typeDict )
    # fltrType = int( input( ) )
    # if fltrType == 1:
    #     clear( 2 )
    #     levelDict = { 0: 'Select Filter Intensity:',
    #             1: 'None',
    #             2: 'more than 2 outliers per night',
    #             3: 'more than 3 outliers per night',
    #             4: 'exactly 4 outliers per night' }
    #     menu.display( levelDict )
    #     fltrLvl = int( input( ) )
    # elif fltrType == 2:
    #     fltrLvl = float( input( 
    #         "Rating Filter (ex. enter '90' for 90% chance or more of anomaly ): " ) )
    # elif fltrType == 3:
    #     # TODO: add weighted attribute filtering
    #     print( "Defaulting to no filter..." )
    #     fltrLvl = 0
    # else:
    #     fltrLvl = 0
        
    # return [ fltrType, fltrLvl ]



########################################################################################
### MAIN PROGRAM:
### Inputs: none
### Returns: none
### Use: provides SNAPS menu for navigating through multiple options, including
### run program, view specific asteroid, help, and quit. Allows user to view, analyze,
### and export data on asteroids pulled from the mongo database.
########################################################################################
def main( ):
    maxIn = int( sys.argv[ 1 ] )
    offset = int( sys.argv[ 2 ] )
    fltrType = sys.argv[ 3 ]
    fltrLvl = int( sys.argv[ 4 ] )
    fltr = [ fltrType, fltrLvl ]
    plots = sys.argv[ 5 ]
    exportFlg = sys.argv[ 6 ]
    # wantedAttrs = sys.argv[ 7 ]
    
    # defaults of these for the versions that don't set them themselves
    exportArgs = [2, ""]
    astArgs = [0, 'n', 0, 0]

    # annoying handling of boolean inputs - may change this later
    exportFlg = [ False, True ][ exportFlg.lower()[0] == "t" ]
    plots = [ False, True ][ plots.lower()[0] == "t" ]

    # initialize astData object and some variables
    astData = AstData()
    astData.setupAttrs( wantedAttrs, ['jd', 'id', 'ssnamenr'] )
    astData.setMaxIn( maxIn )
    astData.setOffset( offset )

    if len(sys.argv) <= 7:
        pass
        # exportArgs = [ 2, "" ]
        # astArgs = [ 0, 'n', 0, 0 ]
        astData.setAstNames()        
    else:
        # out.help()
        if exportFlg:
            exportArgs = [ int( sys.argv[ 7 ] ),
                           sys.argv[ 8 ] ]
            astData.setAstNames()
            if maxIn == 1:
                astArgs = [ int( sys.argv[ 9 ] ),
                            sys.argv[ 10 ],
                            int( sys.argv[ 11 ] ),
                            int( sys.argv[ 12 ] ) ]
                astData.names.append( int( sys.argv[ 9 ] ) )
                print( astData.names )
        else:
            astArgs = [ int( sys.argv[ 7 ] ),
                        sys.argv[ 8 ],
                        int( sys.argv[ 9 ] ),
                        int( sys.argv[ 10 ] ) ]
            astData.names.append( int( sys.argv[ 7 ] ) )

    if fltrType == "anomaly":
        if maxIn == 1:
            oneAst.view( astData, astArgs, exportFlg, exportArgs, fltr, plots )
        else:
            multAst.run( astData, exportFlg, exportArgs, fltr, plots )
            
    elif fltrType == "dbscan":
        dbscan.runDBSCAN( astData, plots, exportFlg )
    elif fltrType == "isoforest":
        forest.runIForest( astData, plots, exportFlg )
    else:
        print("ERROR: Incorrect filter type given. Please choose from the following:" )
        print( fltrTypeMsg )

## Run the program #####################################################################
main( )
leave( )
