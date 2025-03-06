#########################################################################################
### Program: ADAPT (Anomaly Detection for Asteroid Patterns and Trends)
### Programmer: Savannah Chappus
### Last Update: 2.21.2025
###
### File: dbscanADAPT.py
### Use: handles logic for connecting to the mongo database for ZTF data
#########################################################################################

## IMPORTS ##############################################################################
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import Normalizer
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib.patches as mpatches
import mplcursors

## Custom Imports ##
from mongoConnection import Mongo
import getObservations as getObs
import getPostage as postage
import output as out

def float_range( start, stop, step, precision=2 ):
    while start < stop:
        yield round( start, precision )
        start += step

def preProcess( astData, name ): # will take cols as input later
    scaler = Normalizer()
    data = pd.DataFrame( astData.mag18.find( { "ssnamenr": int( name ) } ) )
    sortedDF = astData.sort( data, "jd" )
    df = astData.trimToCols( sortedDF, ["rb", "elong", "mag18omag8"] )
    dataArray = df.to_numpy()
    normData = scaler.fit_transform( dataArray )
    return sortedDF, dataArray, normData
    

# data needs to be trimmed to desiredCols (1 asteroid at a time)
def runDBSCAN( astData, plots, export ): # not sure if eps and minPts should be passed here or calculated later
    # attemting to modify this to run multiple also:
    names = astData.names
    for astName in names:
        # astName = astData.names[0] # for now
        untrimmed, unnorm, data = preProcess( astData, astName )

        e = 0.04 # starting point
        minPts = 3 # starting point

        tune = False
        stamps = False
        if tune:
            paramTune( astData, astName, plots, export )
        else:
            db = DBSCAN(eps=e, min_samples=minPts ).fit( data )
            labels = db.labels_
            clusters = db.fit_predict(data)
            clusterSizes = Counter( clusters )

            if ( plots ):
                extraStuff = [ minPts, e, clusterSizes ]
                plotDBSCAN( labels, db, extraStuff, unnorm, astName, export )

            clusterData = fetchDataForCluster( 1, untrimmed, labels, astName, astData.dataCols, export )

            getObs.getAll( astName, untrimmed, astData.dataCols, export )
            if ( export ):
                out.exportFile( 3, str(astName) + "clusterData", clusterData )
            else:
                out.screenDisplay( clusterData, "Cluster Data" )

            if ( stamps ):
                postage.fromDF( clusterData )


def paramTune( astData, astName, plots, export ):
    # astName = astData.names[0] # for now
    untrimmed, unnorm, data = preProcess( astData )

    for e in float_range( 0.01, 0.1, 0.01 ):
        for minPts in range( 3, 10, 2):
            db = DBSCAN(eps=e, min_samples=minPts ).fit( data )
            labels = db.labels_
            clusters = db.fit_predict(data)
            clusterSizes = Counter( clusters )

            if ( plots ):
                extraStuff = [ minPts, e, clusterSizes ]
                plotDBSCAN( labels, db, extraStuff, unnorm, astName, export )

        

def plotDBSCAN( labels, db, extras, data, astName, export ):
    minPts, e, clusterSizes = extras
    unique_labels = set(labels)
    core_samples_mask = np.zeros_like(labels, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    legendEntries = []

    n_clusters_ = len( set( labels ) ) - ( 1 if -1 in labels else 0 )
    n_noise_ = list( labels ).count( -1 )

    fig = plt.figure()
    ax = fig.add_subplot( projection="3d" )

    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]

        class_member_mask = labels == k

        xyz = data[class_member_mask & core_samples_mask]
        ax.scatter(
            xyz[:, 0],
            xyz[:, 1],
            xyz[:, 2],
            color=tuple(col),
            edgecolors="k",
            s=100,
        )

        xyz = data[class_member_mask & ~core_samples_mask]
        ax.scatter(
            xyz[:, 0],
            xyz[:, 1],
            xyz[:, 2],
            color=tuple(col),
            edgecolors="k",
            s=40,
        )

        # formatting for color/numPts legend
        clusterSize = np.sum( labels == k )
        labelText = f"{clusterSize} pts"
        patch = mpatches.Patch( color=col, label=labelText )
        if len( legendEntries ) <= 15:
            legendEntries.append( patch )


    ax.set_xlabel( "rb" )    
    ax.set_ylabel( "elong" )
    ax.set_zlabel( "mag18omag8" )
    ax.set_title(f"{astName}")

    ax.set_xlim(np.min(data[:, 0]), np.max(data[:, 0]))
    ax.set_ylim(np.min(data[:, 1]), np.max(data[:, 1]))
    ax.set_zlim(np.min(data[:, 2]), np.max(data[:, 2]))
    ax.invert_yaxis()
    ax.invert_xaxis()
    # ax.invert_zaxis()

    noisePercent = ( n_noise_ / len( labels ) ) * 100

    metadataText = ( f"Clusters: {n_clusters_}\n"
                     f"Noise: {noisePercent:.2f}%\n"
                     f"MinPts: {minPts}\n"
                     f"Epsilon: {e}" )

    # clusters & noise, top left
    fig.text( 0.02, 0.98,
              metadataText,
              fontsize=10,
              verticalalignment='top',
              bbox=dict( boxstyle="round,pad=0.3", edgecolor="black", facecolor="white" ) )

    # cluster color & num pts, top left (under previous)
    legend = fig.legend( handles=legendEntries,
                loc="outside left upper",
                bbox_to_anchor=( 0, 0.84 ),
                title="Cluster Sizes",
                fontsize=10,
                title_fontsize=11 )
    legend.get_frame().set_edgecolor("black")
    

    if export:
        ext = "(" + str(minPts) + "-" + str(e) + ")"
        filePath = "/home/sjc497/ADAPT/pngs/"
        fig.savefig( filePath + str(astName) + "dbscan" + ext + ".png" )
        plt.close()
    else:
        # doesn't work right now -- need to figure out what correct data to pass is.
        # cursor = mplcursors.cursor( hover=True )
        # cursor.connect( "add", lambda sel: sel.annotation.set_text( data[ "id" ].iloc[ sel.index ] ) )
        plt.show( block=True )
        fig.show()



def fetchDataForCluster( clusterNum, data, labels, name, cols, exportFlg ):
    clusterData = data[ labels == clusterNum ]
    data = getObs.getSelect( name, clusterData, data, cols, exportFlg )
    return data


# Notes:
# must be able to take any number of parameters
# takes in unfiltered, untrimmed data for processing
# smallest cluster at end is the outlier cluster
