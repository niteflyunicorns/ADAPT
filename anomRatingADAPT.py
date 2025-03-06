#########################################################################################
### Program: ADAPT (Anomaly Detection for Asteroid Patterns and Trends)
### Programmer: Savannah Chappus
### Last Update: 2.7.2025
###
### File: anomRatingADAPT.py
### Use: handles all functions and logic for the anomaly rating filtering system
###      see README.md for more information on the anomaly rating system
#########################################################################################

### IMPORTS #############################################################################
import pandas as pd
import statistics as stat
import numpy as np
import matplotlib.pyplot as plt

### VARIABLES ###########################################################################
wantedAttrs = [ "elong", "rb", "H", "mag18omag8" ] # attributes we want to look at
# wantedAttrs = [ ]
dataCols = wantedAttrs.copy()
dataCols.extend( [ 'jd', 'id', 'ssnamenr' ] ) # additional cols needed for processing
# numFeatures = len( wantedAttrs )
ztfIDS = list( ) # list for associated ztf id for observation
weightDict = {
    "H": 1,
    "mag18omag8": 1,
    "elong": 1,
    "rb": 1
} # all set to one doesn't do much right now...

### FUNCTIONS ###########################################################################
# normValue: takes element to normalize, min, and max values and normalizes to [ 0,1 ]
#@profile
def normValue( value, minVal, maxVal ):
    normVal = ( value - minVal ) / ( maxVal - minVal )
    return normVal

# normDataset: takes in dataset (need not be single-column ) and normalizes
# to range [ 0,1 ]
#@profile
def normDataset( astData ):
    normalizedData = astData.copy( )
    for col in wantedAttrs:
        sortedData = astData.sort_values( by = [ col ] )
        minVal = sortedData[ col ].iloc[ 0 ]
        maxVal = sortedData[ col ].iloc[ len( sortedData ) - 1 ]
        for row in range( len( astData[ col ] ) ):
            newVal = normValue( astData[ col ][ row ], minVal, maxVal )
            normalizedData.loc[ row, col ] = newVal
    return normalizedData

# getObsRating: helper function to getAllObsRatings responsible for getting the
# rating for a single observation for an asteroid
#@profile
def getObsRating( attr, row ):
    obsRating = 0
    for val in row:
        if attr in [ "elong", "mag18omag8" ]:
            obsRating += float( val )
        else:
            obsRating += float( 1 - val )
    # return obsRating
    return ( obsRating / 3 ) # hardcoded: needs to be number of wanted attributes

# getAllObsRatings: helper function to getAstRating responsible for getting
# the ratings for all observations for a given asteroid
#@profile
def getAllObsRatings( data, attr ):
    ratings = [ ]
    for ind, row in data.iterrows():
        obsRating = getObsRating( attr, row )
        ratings.append( obsRating )
    return ratings

# getAstRating: provides a rating for an asteroid based on highest observation
# rating for the asteroid based on outliers
#@profile
def getAstRating( inData, plots, export ):
    # plots = False
    ratings = [ ]
    frames = [ ]
    newAttrs = [ 'elong', 'rb', 'mag18omag8' ]
    data = inData[ dataCols ]
    for attr in newAttrs:
        sortedData = data.sort_values( by = [ attr ] )
        ratingsData = sortedData[ 'jd' ]
        normData = normDataset( sortedData )
        ratings = getAllObsRatings( normData[ newAttrs ], attr )

    ratingsDF = pd.DataFrame( data=ratings, columns=[ 'ratings' ] )
    ratingsData = pd.concat( [ ratingsDF, ratingsData ], axis=1, join='inner' )

    if plots:
        plotData = ratingsData.sort_values( by = ['jd'] )
        plotAstRatings( data[ 'ssnamenr' ][ 0 ], plotData[ 'jd' ], plotData[ 'ratings' ], "jd", "rating", export )

    astRating = max( ratings ) * 100
    print( "Max Rating Index: " + str( ratings.index( max( ratings ) ) ) )
    return ratings, astRating

# plotAstRating: plots the ratings for each observation of an asteroid as collected
# in getAllObsratings
#@profile
def plotAstRatings( name, xData, yData, xName, yName, export ):
    plt.clf()
    plt.title( "Asteroid " + str( name ) )
    plt.scatter( xData, yData, color = 'deeppink' )
    plt.xlabel( xName )
    plt.ylabel( yName )
    plt.ylim( 0, 1 )

    if export:
        savefile = str( name ) + "-ratings.png"
        plt.savefig( savefile )
    else:
        ### TODO ###
        # modify these two lines so that the annotation
        # on hover states the elong, mag18, and rb
        # values for that date. Maybe also include the
        # actual value of the rating...?
        # cursor = mplcursors.cursor( hover=True )
        # cursor.connect( "add", lambda sel: sel.annotation.set_text( data[ "jd" ].iloc[ sel.index ] ) )
        plt.show( block=True )
        plt.show()
        pass

        
# fillSigmaMatrix: takes the name of an asteroid, its data table, and an
# empty matrix to fill with sigma data. Computes sigmas for each attribute
# and stores them in the matrix. Returns the sigma matrix and data regarding
# the night of each observation's max sigma value
#@profile
def fillSigmaMatrix( name, asteroid, sigmaMatrix, fltr, outFlag, plot, export ):
    attrData = [ ]
    obsData = [ ]
    outliers = [ ]
    outliersLoc = [ ]
    outlierNorms = [ ]
    stripFlag = False
    fltrType = fltr[ 0 ]
    fltrLevel = fltr[ 1 ]

    # reset attributes looked at
    attr_ct = 0
    rowSum = absRowSum = 0

    while ( attr_ct < len( wantedAttrs ) ):
        # grab feature data and calculate mean and standard deviation
        feature = wantedAttrs[ attr_ct ]
        try: 
            obj_stdev = stat.stdev( asteroid[ feature ] )
            obj_mean = stat.mean( asteroid[ feature ] )
        except Exception as e:
            print( ( str(name) + " is the object causing error" ), e )
            
        # grab weight for feature
        attr_weight = weightDict[ feature ]

        # sort specific asteroid data by feature & normalize
        # dataSortedByFeature = pd.DataFrame( 
            # mag18Data.find( { "ssnamenr": int( name ) } ).sort( feature ) )
        # dataSortedByFeature = pd.DataFrame( 
            # mag18Data.find( { "ssnamenr": int( name ) } ) )
        asteroid.sort_values( by = [ feature ] )

        # print( asteroid )
        # normData = normDataset( dataSortedByFeature )

        # calculate min, max, and ranges for highSigma and lowSigma values
        minIndex = 0
        maxIndex = len( asteroid ) - 1

        minVal = ( asteroid[ feature ][ minIndex ] )
        maxVal = ( asteroid[ feature ][ maxIndex ] )

        upperRange = maxVal - obj_mean
        lowerRange = obj_mean - minVal

        highSigma = upperRange / obj_stdev
        lowSigma = lowerRange / obj_stdev

        featObsDF = asteroid[ [ feature, "jd" ] ]

        
        # add data to sigmaMatrix
        if ( highSigma > lowSigma ):
            # jd of observation
            obs = asteroid[ "jd" ][ maxIndex ]

            rowSum += highSigma * attr_weight
            absRowSum += highSigma * attr_weight

            # keep track of ant id with specific observation
            ztfIDS.append( asteroid[ 'id' ][ maxIndex ] )
            attrData.append( highSigma * attr_weight )

            # store outliers
            outliers.append( maxVal )

            # calculations for filtering ( opt 2 )
            # outlierNorms.append( normData[ feature ][ maxIndex ] )

        else:
            obs = asteroid[ "jd" ][ minIndex ]
            rowSum += -lowSigma * attr_weight
            absRowSum += lowSigma * attr_weight

            # keep track of ant id with specific observation
            ztfIDS.append( asteroid[ 'id' ][ minIndex ] )
            attrData.append( -lowSigma * attr_weight )

            # store outliers
            outliers.append( minVal )

            # calculations for filtering ( opt 2 )
            # outlierNorms.append( normData[ feature ][ minIndex ] )

        # update attribute count
        attr_ct += 1
        # add jd of sigma value to list
        obsData.append( obs )

    rowAttrs = [ ]
    numZeros = 0

    #### FILTERING DATA ####
    if fltrType == "numpernight":
        # Option 1: filter by number of times outliers occur during single observation
        for obs in range( len( obsData ) ):
            if obsData.count( obsData[ obs ] ) >= fltrLevel:
                rowAttrs.append( attrData[ obs ] )
            else:
                rowAttrs.append( 0 )
                numZeros += 1
        if numZeros > fltrLevel:
            stripFlag = True        
    elif fltrType == "anomaly":
        # Option 2: filter by specifications
        # assigns rating to each asteroid on how likely they are to be anomalous
        # each category is normalized to [ 0,1 ] and the outlying point is rated from
        # 1 to 100 for each category. Then, scores for each category are averaged to get
        # total score for the asteroid. ## TODO ( optional ): incorporate weighting system
        rowAttrs = attrData
        ratings, astRating = getAstRating( asteroid, plot, export )
        
        if astRating < fltrLevel:
            stripFlag = True
    elif fltrType == "sigweight":
        # Option 3: filter by weight
        ### TODO: Write filter by weight option
        pass
    else:
        pass

    # setting rowAttrs and astRating
    if fltrType != "anomaly":
        astRating = np.nan
    if fltrType in [ "sigweight", "none" ]:
        rowAttrs = attrData

    rowAttrs.append( rowSum )
    rowAttrs.append( absRowSum )
    rowAttrs.append( astRating )
    
    sigmaMatrix = rowAttrs
    if stripFlag:
        sigmaMatrix = [ ]

    if outFlag:
        return ( sigmaMatrix, obsData, ztfIDS, outliers )

    return ( sigmaMatrix, obsData, ztfIDS )
