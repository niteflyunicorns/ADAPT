#########################################################################################
### Program: ADAPT (Anomaly Detection for Asteroid Patterns and Trends)
### Programmer: Savannah Chappus
### Last Update: 2.8.2025
###
### File: viewMultAst.py
### Use: handles logic for viewing data for more than one asteroid given via command line
#########################################################################################

### IMPORTS #############################################################################
import numpy as np
import pandas as pd

## Custom imports ##
from mongoConnection import Mongo
import plotting as plot
import output as out
import anomRatingADAPT as anomaly

### VARIABLES ###########################################################################
mongo = Mongo()
asteroidData = mongo.getData( 'asteroids_all' )
mag18Database = mongo.getData( 'mag18o8' )
wantedAttrs = [ "elong", "rb", "H", "mag18omag8" ] # attributes we want to look at
dataCols = wantedAttrs.copy()
dataCols.extend( [ 'jd', 'id', 'ssnamenr' ] ) # additional cols needed for processing
numFeatures = len( wantedAttrs )
ztfIDS = list( ) # list for associated ztf id for observation
weightDict = {
    "H": 1,
    "mag18omag8": 1,
    "elong": 1,
    "rb": 1
}

#########################################################################################
### RUN function
### Inputs: none
### Returns: none
### Use: runs the program from menu option 1. Lets users view as many asteroids
### as desired from any starting point in the data, then computes and fills the sigma
### matrix and runs data analytics on the results.
#########################################################################################
#@profile
def run( maxIn, offset, exportFlg, exportArgs, fltrType, fltrLvl, plots ):
    # total num of asteroids we want to look at
    #maxIn = int( input( "How many asteroids do you want to look at( -1 if all ): " ) )
    
    # get all asteroid names
    asteroidNames = pd.DataFrame( asteroidData.find( {},{ '_id': 0, 'ssnamenr' : 1 } ) )
    fileType, fileName = exportArgs

    featFltr = 'n'
    if ( maxIn < 0 ) :
        # print(asteroidData)
        maxIn = asteroidNames.size
        print( "WARNING: This will run all " + str( maxIn ) + " asteroids through the program." )
        # print( "This process may take several hours depending on your system.\n" )
        # if ( input( "Continue (y/n)? " ) == 'n' ):
            # exit()
        # allAstMenu = { 0: 'What would you like to do?',
        #         1: 'Run and display output on screen',
        #         2: 'Run and export output to file',
        #         3: 'Cancel' }
        # menu.display( allAstMenu )
        # allAstDecision = int( input( ) )
        # if allAstDecision == 3:
        # runProgram( )
        # if allAstDecision == 2:
            # exportFlg = 'y'
             
    #offset = int( input( "Where to start in data:( -1 if random ):  " ) )
    
    if ( offset < 0 and maxIn < asteroidData.count( ) ):
        offset = rand.randint( 0, asteroidData.count( ) - maxIn - 1 )

    # exportFlg = input( "Would you like to export the results ( y/n )? " )

    # if exportFlg == 'y':
        # fileType =  int( input( "Export as \n 1. .html \n 2. .csv \n" ) )
        # filename = input( "filename: " )

    # fltr = getFilter( )
    fltr = [ fltrType, fltrLvl ]
        
    # num of asteroids we have looked at 
    ast_ct = 0

    #Sigma Matrix
    extraCols = 3 # for: rowSum, absRowSum, asteroidRating
    sigmaMatrix = np.zeros( [ maxIn, numFeatures + extraCols ] )

    # necessary data from database
    # print( "asteroidNames \n" )
    # astNamesArr = asteroidNames[ "ssnamenr" ][:maxIn].values.tolist()
    # print( astNamesArr )
    # mag18DataNew = pd.DataFrame( mag18Database.find( { "ssnamenr": { "$in": astNamesArr } }, { "id": 1, "ssnamenr": 1, "jd": 1, "elong": 1, "rb": 1, "H": 1, "mag18omag8": 1, "night": 1 } ) )
    # print( mag18DataNew )

    # Loop through our collection of names
    while ( ast_ct < maxIn and ast_ct < len( asteroidNames ) ):
        # create temporary row variable to hold asteroid data for appending at the end
        attrData = [ ]
        obsData = [ ]
        arrayOffset = ast_ct + offset

        # grab asteroid name
        name = asteroidNames[ "ssnamenr" ][ arrayOffset ]

        # reset attributes looked at
        attr_ct = 0

        # sort specific asteroid data by Julian Date
        mag18Data = pd.DataFrame( mag18Database.find( { "ssnamenr": int( name ) } ) )
        mag18Data = mag18Data[ dataCols ]
        # mag18Data = mag18DataNew
        asteroid = mag18Data.sort_values( by = [ "jd" ] )
        attrData, obsData, ztfIDS = anomaly.fillSigmaMatrix( name, asteroid, sigmaMatrix, fltr, False, plots, exportFlg )
        
        if len( attrData ) != 0:
            sigmaMatrix[ ast_ct ] = attrData

        # update asteroid count
        ast_ct += 1

        if plots:
            plot.plot3Das2D( name, asteroid['rb'],
                        asteroid['elong'],
                        asteroid['mag18omag8'],
                        "rb", "elong", "mag18omag8",
                        asteroid, exportFlg )
        
            plot.plot3Dand2D( name, asteroid['rb'],
                         asteroid['elong'],
                         asteroid['mag18omag8'],
                         "rb", "elong", "mag18omag8",
                         asteroid, exportFlg )

    # Reset arrays for rerunning program
    nameArray = [ ]
    listNames = [ ]
    idArray = [ ]
        
    # Formatting data structures
    arrayOffset = offset + ast_ct
    nameArray = np.array( asteroidNames[ 'ssnamenr' ] )[ offset: arrayOffset ]

    dataset = out.formatDataTable( sigmaMatrix, ztfIDS, nameArray, maxIn, numFeatures )

    # clear ztfIDS for next use
    ztfIDS.clear( )

    # EXPORT
    # drop all rows in data where zeros are present ( from filters )
    ### WARNING: I'm not sure if this works with the new filter system
    ### TODO: check if it works and fix if it doesn't
    newData = dataset.drop( 
        dataset.query( "rb==0 and elong==0 and H==0 and mag18omag8==0" ).index )
    if exportFlg:
        out.exportFile( fileType, fileName, newData )
    else:
        print( newData )
    
    # first printout of relevant asteroid data
    # if ( input( "Look at total data histogram ( y/n ): " ) == 'y' ):
    if ( plots ):
        # totalHistFigs, plts = plt.subplots( 2, 3, figsize=( 15,15 ) )
        # totalHistFigs.suptitle( "Histograms" )

        # # print( "Row Sum Histogram" )
        # plts[ 0,0 ].hist( np.array( dataset[ "Row Sum" ] ) )
        # plts[ 0,0 ].set( xlabel = "num sigmas", ylabel = "num asteroids", title = "Row Sum" )

        # elongTest = dataset[ 'elong' ].sum( )
        # rbTest = dataset[ 'rb' ].sum( )
        # hTest = dataset[ 'H' ].sum( )
        # mag18 = dataset[ 'mag18omag8' ].sum( )

        # elongTestM = dataset[ 'elong' ].mean( )
        # rbTestM = dataset[ 'rb' ].mean( )
        # hTestM = dataset[ 'H' ].mean( )
        # mag18M = dataset[ 'mag18omag8' ].mean( )


        # print( "ELONG" )
        # print( "Sum :" + str( elongTest ) )
        # print( "Mean:" + str( elongTestM ) )
        # plts[ 0,1 ].hist( np.array( dataset[ "elong" ] ) )
        # plts[ 0,1 ].set( xlabel = "num sigmas",
        #               ylabel = "num asteroids",
        #               title = "ELONG" )

        # print( "RB" )
        # print( "Sum :" + str( rbTest ) )
        # print( "Mean:" + str( rbTestM ) )
        # plts[ 0,2 ].hist( np.array( dataset[ "rb" ] ) )
        # plts[ 0,2 ].set( xlabel = "num sigmas",
        #               ylabel = "num asteroids",
        #               title = "RB" )

        # print( "H" )
        # print( "Sum :" + str( hTest ) )
        # print( "Mean:" + str( hTestM ) )
        # plts[ 1,0 ].hist( np.array( dataset[ "H" ] ) )
        # plts[ 1,0 ].set( xlabel = "num sigmas",
        #               ylabel = "num asteroids",
        #               title = "H" )

        # print( "MAG18OMAG8" )
        # print( "Sum :" + str( mag18 ) )
        # print( "Mean:" + str( mag18M ) )
        # plts[ 1,1 ].hist( np.array( dataset[ "mag18omag8" ] ) )
        # plts[ 1,1 ].set( xlabel = "num sigmas",
        #               ylabel = "num asteroids",
        #               title = "MAG18OMAG8" )

        # # adjust the spacing so things don't overlap
        # totalHistFigs.subplots_adjust( 
        #                     wspace=0.4,
        #                     hspace=0.4 )

        # # delete currently unused 6th plot space
        # totalHistFigs.delaxes( plts[ 1,2 ] )

        # # show the total histogram plots
        # totalHistFigs.show( )
        pass

    ### FOR PROGRAMMERS: the below are "ideal" filter levels for each attribute
    ### this data is subjective and open to change. Additionally, this filtering
    ### method has essentially been replaced by the anomaly rating
    # rbLowFlag = dataset[ dataset[ 'rb' ] <= -4 ]
    # rbHighFlag = dataset[ dataset[ 'rb' ] >= 0 ]
    # HHighFlag = dataset[ dataset[ 'H' ] >= 3 ]
    # HLowFlag = dataset[ dataset[ 'H' ] <= -4 ]
    # elongHighFlag = dataset[ dataset[ 'elong' ] >= 4 ]

    # filtering loop for individual attributes
    filteredDataset = dataset
    emptyFlag = False
    continueFlag = ( featFltr != 'n' ) # will not start if no featFltr was given at start

    while ( continueFlag and( not emptyFlag ) ):
        # filterInput = input( "Enter feature to filter by( 'n' if None ): \n" )
        # continueFlag = ( filterInput != 'n' )

        if ( continueFlag ):
            filterHighLimit = int( input( "Data >  " ) )
            filterLowLimit = int( input( "Data <  " ) )

            prevSet = filteredDataset
            filteredDataset = filteredDataset.loc[ 
                ( filteredDataset[ filterInput ] > filterHighLimit ) &
                ( filteredDataset[ filterInput ] < filterLowLimit ) ]
            emptyFlag = filteredDataset.empty

            if ( not emptyFlag ):
                print( filteredDataset )

            else:
                print( "This returns an empty Data Set " )

                resetInput = int( input( 
                    "0 to continue, 1 to reset last filter, 2 to reset all filters" ) )

                if ( resetInput == 1 ):
                    filteredDataset = prevSet
                    emptyFlag = False
                    continueFlag = True

                if ( resetInput == 2 ):
                    filteredDataset = dataset
                    emptyFlag = False
                    continueFlag = True

    # prompt for inspecting specific asteroid after running program on multiple
    # if ( input( "Inspect Specific Asteroid( y/n ): " ) == "y" ):
        # viewOne( )
