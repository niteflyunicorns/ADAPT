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
import plotting as plot
import output as out
import anomRatingADAPT as anomaly

### VARIABLES ###########################################################################

#########################################################################################
### RUN function
### Inputs: none
### Returns: none
### Use: runs the program from menu option 1. Lets users view as many asteroids
### as desired from any starting point in the data, then computes and fills the sigma
### matrix and runs data analytics on the results.
#########################################################################################
#@profile
# def run( astData, maxIn, offset, exportFlg, exportArgs, fltrType, fltrLvl, plots ):
def run( astData, exportFlg, exportArgs, fltr, plots ):
    fileType, fileName = exportArgs
    astData.setAstNames()
    print( astData.names )
    featFltr = 'n' # not sure what this is doing
    # num of asteroids we have looked at 
    ast_ct = 0

    #Sigma Matrix
    extraCols = 3 # for: rowSum, absRowSum, asteroidRating
    sigmaMatrix = np.zeros( [ astData.maxIn, astData.numFeatures + extraCols ] )

    # Loop through our collection of names
    while ( ast_ct < astData.maxIn and ast_ct < len( astData.names ) ):
        # create temporary row variable to hold asteroid data for appending at the end
        attrData = [ ]
        obsData = [ ]
        arrayOffset = ast_ct + astData.offset
        # grab asteroid name
        name = astData.names[ arrayOffset ]
        # reset attributes looked at
        attr_ct = 0
        # sort specific asteroid data by Julian Date
        mag18Data = pd.DataFrame( astData.mag18.find( { "ssnamenr": int (name ) } ) )
        asteroid = astData.sort( astData.trimToCols( mag18Data, astData.dataCols ), "jd" )

        # filtering for anomaly
        attrData, obsData, astData.ztfIDS = anomaly.fillSigmaMatrix( name, asteroid, sigmaMatrix, fltr, False, plots, exportFlg )

        # post-processing
        if len( attrData ) != 0:
            sigmaMatrix[ ast_ct ] = attrData

        # update asteroid count
        ast_ct += 1

        # display results
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
    arrayOffset = astData.offset + ast_ct
    nameArray = np.array( astData.names )[ astData.offset: arrayOffset ]

    dataset = out.formatDataTable( sigmaMatrix, astData.ztfIDS, nameArray, astData.maxIn, astData.numFeatures )

    # clear ztfIDS for next use
    astData.ztfIDS.clear( )

    # EXPORT
    if exportFlg:
        out.exportFile( fileType, fileName, newData )
    else:
        for ast in range(astData.maxIn):
            print( dataset.transpose( ) )
            print()
    
    # first printout of relevant asteroid data
    if ( plots ):
        pass



# STUFF TO SAVE FOR LATER

    # if ( maxIn < 0 ) :
    #     maxIn = astData.names.size
    #     print( "WARNING: This will run all " + str( maxIn ) + " asteroids through the program." )
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

    
### FOR PROGRAMMERS: the below are "ideal" filter levels for each attribute
### this data is subjective and open to change. Additionally, this filtering
### method has essentially been replaced by the anomaly rating
# rbLowFlag = dataset[ dataset[ 'rb' ] <= -4 ]
# rbHighFlag = dataset[ dataset[ 'rb' ] >= 0 ]
# HHighFlag = dataset[ dataset[ 'H' ] >= 3 ]
# HLowFlag = dataset[ dataset[ 'H' ] <= -4 ]
# elongHighFlag = dataset[ dataset[ 'elong' ] >= 4 ]


# filtering loop for individual attributes
    # filteredDataset = dataset
    # emptyFlag = False
    # continueFlag = ( featFltr != 'n' ) # will not start if no featFltr was given at start

    # while ( continueFlag and( not emptyFlag ) ):
    #     # filterInput = input( "Enter feature to filter by( 'n' if None ): \n" )
    #     # continueFlag = ( filterInput != 'n' )

    #     if ( continueFlag ):
    #         filterHighLimit = int( input( "Data >  " ) )
    #         filterLowLimit = int( input( "Data <  " ) )

    #         prevSet = filteredDataset
    #         filteredDataset = filteredDataset.loc[ 
    #             ( filteredDataset[ filterInput ] > filterHighLimit ) &
    #             ( filteredDataset[ filterInput ] < filterLowLimit ) ]
    #         emptyFlag = filteredDataset.empty

    #         if ( not emptyFlag ):
    #             print( filteredDataset )

    #         else:
    #             print( "This returns an empty Data Set " )

    #             resetInput = int( input( 
    #                 "0 to continue, 1 to reset last filter, 2 to reset all filters" ) )

    #             if ( resetInput == 1 ):
    #                 filteredDataset = prevSet
    #                 emptyFlag = False
    #                 continueFlag = True

    #             if ( resetInput == 2 ):
    #                 filteredDataset = dataset
    #                 emptyFlag = False
    #                 continueFlag = True

