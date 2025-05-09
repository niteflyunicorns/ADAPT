#########################################################################################
### Program: ADAPT (Anomaly Detection for Asteroid Patterns and Trends)
### Programmer: Savannah Chappus
### Last Update: 3.06.2025
###
### File: isoforestADAPT.py
### Use: handles logic for Isolation Forest filtering system
#########################################################################################

## IMPORTS ##############################################################################
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import Normalizer
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors

## Custom Imports ##
from mongoConnection import Mongo
import getObservations as getObs
import getPostage as postage
import output as out

## Global Variables ##
feats = [ "elong", "rb", "mag18omag8" ]

def float_range( start, stop, step, precision=2 ):
    while start < stop:
        yield round( start, precision )
        start += step

def preProcess( astData, name ):
    # scaler = Normalizer()
    data = pd.DataFrame( astData.mag18.find( { "ssnamenr": int( name ) } ) )
    sortedDF = astData.sort( data, "jd" )
    df = astData.trimToCols( sortedDF, feats )
    dataArray = df.to_numpy()
    trainData, testData  = train_test_split( dataArray, random_state=42 )
    # normData = scaler.fit_transform( dataArray )
    return sortedDF, trainData, testData 


def fetchDataForCluster( clusterNum, data, labels, name, cols, exportFlg ):
    clusterData = data[ labels == clusterNum ]
    data = getObs.getSelect( name, clusterData, data, cols, exportFlg )
    return data


def runIForest( astData, plots, exportFile, export ):
    names = astData.names
    for astName in names:
        untrimmed, trainData, testData = preProcess( astData, astName )
        features = untrimmed[ feats ]

        state = 0 # starting point

        tune = False
        stamps = False
        if tune:
            paramTune( astData, astName, plots, export )
        else:
            clf = IsolationForest( random_state=state )
            clf.fit( features )
            trimmed = untrimmed.loc[ features.index ].copy()
            trimmed[ 'anomalyScore' ] = clf.decision_function( features )
            trimmed[ 'anomaly' ] = clf.predict( features )

            anomData = trimmed[ trimmed[ 'anomaly' ] == -1 ]
            normData = trimmed[ trimmed[ 'anomaly' ] == 1 ]
                
            if ( plots ):
                plotIForest( trimmed, astName, export )

            if ( export ):
                filename = exportFile + "isoforest/" + str(astName) 
                out.exportFile( 3, filename + "-anomaly", anomData[ astData.dataCols ] )
                out.exportFile( 3, filename + "-normal", normData[ astData.dataCols ] )
            else:
                pass
                # currently screenDisplay is not working
                # out.screenDisplay( normData[ astData.dataCols ], "Normal Data" )
                # out.screenDisplay( anomData[ astData.dataCols ], "Anomalous Data" )

            if ( stamps ):
                postage.fromDF( clusterData )


def paramTune( astData, astName, plots, export ):
    pass
    # astName = astData.names[0] # for now
    # data = preProcess( astData )

    # for e in float_range( 0.01, 0.1, 0.01 ):
    #     for minPts in range( 3, 10, 2):
    #         db = DBSCAN(eps=e, min_samples=minPts ).fit( data )
    #         labels = db.labels_
    #         clusters = db.fit_predict(data)
    #         clusterSizes = Counter( clusters )

    #         if ( plots ):
    #             extraStuff = [ minPts, e, clusterSizes ]
    #             plotDBSCAN( labels, db, extraStuff, data, astName, export )

        

def plotIForest( data, astName, export ):
    normal = data[ data[ 'anomaly' ] == 1 ]
    anomalies = data[ data[ 'anomaly' ] == -1 ]

    fig = plt.figure()
    ax = fig.add_subplot( projection="3d" )

    ax.scatter( normal[ "elong" ],
                normal[ "rb" ],
                normal[ "mag18omag8" ],
                label='Normal',
                c="lightcoral",
                edgecolors="k", s=100 )
    ax.scatter( anomalies[ "elong" ],
                anomalies[ "rb" ],
                anomalies[ "mag18omag8" ],
                label='Anomaly',
                c="k",
                edgecolors="k", s=40 )

    ax.set_xlabel( "elong" )    
    ax.set_ylabel( "rb" )
    ax.set_zlabel( "mag18omag8" )
    ax.set_title(f"{astName}")
    fig.legend( loc="outside left upper" )
    

    if export:
        filePath = "/scratch/sjc497/ADAPT/pngs/isoforest/"
        fig.savefig( filePath + str(astName) + "iforest" + ".png" )
        # plt.close()
    else:
        # doesn't work right now -- need to figure out what correct data to pass is.
        # cursor = mplcursors.cursor( hover=True )
        # cursor.connect( "add", lambda sel: sel.annotation.set_text( data[ "id" ].iloc[ sel.index ] ) )
        plt.show( block=True )
        fig.show()

