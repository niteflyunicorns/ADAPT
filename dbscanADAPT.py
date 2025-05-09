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
    df = astData.trimToCols( sortedDF, ["elong", "rb", "mag18omag8"] )
    dataArray = df.to_numpy()
    normData = scaler.fit_transform( dataArray )
    return sortedDF, dataArray, normData


def getClusters( data, labels ):
    clusterLabels = []
    maxSize = 1
    maxClusterLabel = 0
    for k in labels:
        cluster = data[ labels == k ]
        if len( cluster ) > maxSize:
            maxSize = len( cluster )
            maxClusterLabel = k
        if k not in clusterLabels and k != -1:
            clusterLabels.append( k )
    if maxClusterLabel in clusterLabels:
        clusterLabels.remove( maxClusterLabel )

    return clusterLabels


def fetchDataForCluster( clusterNum, data, labels, name, cols, exportFlg ):
    clusterData = data[ labels == clusterNum ]
    data = getObs.getSelect( name, clusterData, data, cols, exportFlg )
    return data


# data needs to be trimmed to desiredCols (1 asteroid at a time)
def runDBSCAN( astData, plots, exportFile, export ): # not sure if eps and minPts should be passed here or calculated later
    # attemting to modify this to run multiple also:
    names = astData.names
    for astName in names:
        untrimmed, unnorm, data = preProcess( astData, astName )

        e = 0.04 # starting point
        minPts = 3 # starting point
        # e = 8.0
        # minPts = 5 # 5 or 7

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

            getObs.getAll( astName, untrimmed, astData.dataCols, exportFile + "dbscan/", export )
            
            COI = getClusters( untrimmed, labels )
            for cluster in COI:
                clusterData = fetchDataForCluster( cluster, untrimmed, labels, astName, astData.dataCols, export )
                if ( export ):
                    filename = exportFile + "dbscan/" + str(astName) + "-dbscan-cluster" + str(cluster)
                    out.exportFile( 3, filename, clusterData[ astData.dataCols ] )
                else:
                    out.screenDisplay( clusterData[ astData.dataCols ], "Cluster " + str( cluster ) + " Data" )

            # if ( stamps ):
            #     postage.fromDF( clusterData )


def paramTune( astData, astName, plots, export ):
    maxScore, goodE, goodPts = 0, 0, 0
    maxScore = 0
    untrimmed, unnorm, data = preProcess( astData, astName )
    for e in float_range( 5, 10.5, 0.5 ): # unnormalized range
    # for e in float_range( 0.05, 1.0, 0.05 ):
        for minPts in range( 5, 9, 2 ):
            score = 0
            db = DBSCAN(eps=e, min_samples=minPts ).fit( unnorm )
            labels = db.labels_
            clusters = db.fit_predict(data)
            clusterSizes = Counter( clusters )

            noise = list( labels ).count( -1 )
            noisePercent = ( noise / len( labels ) ) * 100
            n_clusters = len( set( labels ) ) - ( 1 if -1 in labels else 0 )
            # score results so that we only output one result. 
            if 2 <= n_clusters <= 10:
                score += 2
            elif 10 < n_clusters <= 20:
                score += 1
            else:
                score -= 1

            if 5.0 <= noisePercent <= 30.0:
                score += 2
            else:
                score -= 1

            if score > maxScore:
                maxScore = score
                goodE = e
                goodPts = minPts
    if ( plots ) and goodE != 0 and goodPts != 0:
        extraStuff = [ goodPts, goodE, clusterSizes ]
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


    ax.set_xlabel( "elong" )    
    ax.set_ylabel( "rb" )
    ax.set_zlabel( "mag18omag8" )
    ax.set_title(f"{astName}")

    ax.set_xlim(np.min(data[:, 0]), np.max(data[:, 0]))
    ax.set_ylim(np.min(data[:, 1]), np.max(data[:, 1]))
    ax.set_zlim(np.min(data[:, 2]), np.max(data[:, 2]))
    # ax.invert_yaxis()
    # ax.invert_xaxis()
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
        ext = str(minPts) + "-" + str(e)
        filePath = "/scratch/sjc497/ADAPT/pngs/dbscan/"
        fig.savefig( filePath + str(astName) + "dbscan" + ext + ".png" )
        plt.close()
    else:
        # doesn't work right now -- need to figure out what correct data to pass is.
        # cursor = mplcursors.cursor( hover=True )
        # cursor.connect( "add", lambda sel: sel.annotation.set_text( data[ "id" ].iloc[ sel.index ] ) )
        plt.show( block=True )
        fig.show()

