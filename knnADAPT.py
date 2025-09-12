#########################################################################################
### Program: ADAPT (Anomaly Detection for Asteroid Patterns and Trends)
### Programmer: Savannah Chappus
### Last Update: 9.12.2025
###
### File: knnADAPT.py
### Use: handles logic and functionality for the kNN classification
#########################################################################################

## IMPORTS ##############################################################################
from sklearn.preprocessing import Normalizer
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from collections import Counter
# import matplotlib.patches as mpatches
# import mplcursors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from sklearn.neighbors import NearestNeighbors

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


def chooseK( data ):
    n = len( data )
    # any value that is 5% of the dataset, provided it is between 3 and 50
    # to avoid bad sampling -- this may need to be more complex later
    k = min(max(3, int(n * 0.05)), 50)
    return k

# def getClusters( data, labels ):
#     clusterLabels = []
#     maxSize = 1
#     maxClusterLabel = 0
#     for k in labels:
#         cluster = data[ labels == k ]
#         if len( cluster ) > maxSize:
#             maxSize = len( cluster )
#             maxClusterLabel = k
#         if k not in clusterLabels and k != -1:
#             clusterLabels.append( k )
#     if maxClusterLabel in clusterLabels:
#         clusterLabels.remove( maxClusterLabel )

#     return clusterLabels


# def fetchDataForCluster( clusterNum, data, labels, name, cols, exportFlg ):
#     clusterData = data[ labels == clusterNum ]
#     data = getObs.getSelect( name, clusterData, data, cols, exportFlg )
#     return data


# data needs to be trimmed to desiredCols (1 asteroid at a time)
def runKNN( astData, plots, exportFile, export ):
    names = astData.names
    for astName in names:
        untrimmed, unnorm, data = preProcess( astData, astName )

        # value for k -- generate dynamically based on size of dataset?
        k = chooseK( data )

        tune = False
        stamps = False
        if tune:
            paramTune( astData, astName, plots, export )
        else:
            nbrs = NearestNeighbors( n_neighbors=k+1 ).fit( data )
            distances, _ = nbrs.kneighbors( data )
            densityScores = distances[:, 1:].mean( axis=1 )

            if ( plots ):
                plotKNN( k, densityScores, unnorm, astName, export )

            # getObs.getAll( astName, untrimmed, astData.dataCols, exportFile + "dbscan/", export )
            
            # COI = getClusters( untrimmed, labels )
            # for cluster in COI:
            #     clusterData = fetchDataForCluster( cluster, untrimmed, labels, astName, astData.dataCols, export )
            #     if ( export ):
            #         filename = exportFile + "dbscan/" + str(astName) + "-dbscan-cluster" + str(cluster)
            #         out.exportFile( 3, filename, clusterData[ astData.dataCols ] )
            #     else:
            #         out.screenDisplay( clusterData[ astData.dataCols ], "Cluster " + str( cluster ) + " Data" )

            # if ( stamps ):
            #     postage.fromDF( clusterData )


def paramTune( astData, astName, plots, export ):
    pass
#     maxScore, goodE, goodPts = 0, 0, 0
#     maxScore = 0
#     untrimmed, unnorm, data = preProcess( astData, astName )
#     for e in float_range( 5, 10.5, 0.5 ): # unnormalized range
#     # for e in float_range( 0.05, 1.0, 0.05 ):
#         for minPts in range( 5, 9, 2 ):
#             score = 0
#             db = DBSCAN(eps=e, min_samples=minPts ).fit( unnorm )
#             labels = db.labels_
#             clusters = db.fit_predict(data)
#             clusterSizes = Counter( clusters )

#             noise = list( labels ).count( -1 )
#             noisePercent = ( noise / len( labels ) ) * 100
#             n_clusters = len( set( labels ) ) - ( 1 if -1 in labels else 0 )
#             # score results so that we only output one result. 
#             if 2 <= n_clusters <= 10:
#                 score += 2
#             elif 10 < n_clusters <= 20:
#                 score += 1
#             else:
#                 score -= 1

#             if 5.0 <= noisePercent <= 30.0:
#                 score += 2
#             else:
#                 score -= 1

#             if score > maxScore:
#                 maxScore = score
#                 goodE = e
#                 goodPts = minPts
#     if ( plots ) and goodE != 0 and goodPts != 0:
#         extraStuff = [ goodPts, goodE, clusterSizes ]
#         plotDBSCAN( labels, db, extraStuff, unnorm, astName, export )
        

def plotKNN( k, densityScores, data, astName, export ):
    # minPts, e, clusterSizes = extras
    # unique_labels = set(labels)
    # core_samples_mask = np.zeros_like(labels, dtype=bool)
    # core_samples_mask[db.core_sample_indices_] = True
    legendEntries = []

    # n_clusters_ = len( set( labels ) ) - ( 1 if -1 in labels else 0 )
    # n_noise_ = list( labels ).count( -1 )

    fig = plt.figure()
    ax = fig.add_subplot( projection="3d" )

    # colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
    # for k, col in zip(unique_labels, colors):
    #     if k == -1:
    #         # Black used for noise.
    #         col = [0, 0, 0, 1]

    #     class_member_mask = labels == k

    scplt = ax.scatter(
        data[:, 0],
        data[:, 1],
        data[:, 2],
        c=densityScores,
        cmap="magma",
        s=50,
    )

        # # formatting for color/numPts legend
        # clusterSize = np.sum( labels == k )
        # labelText = f"{clusterSize} pts"
        # patch = mpatches.Patch( color=col, label=labelText )
        # if len( legendEntries ) <= 15:
        #     legendEntries.append( patch )


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

    # noisePercent = ( n_noise_ / len( labels ) ) * 100

    avgDensity = round( np.mean( densityScores ), 2 )
    minDensity = round( np.min( densityScores ), 2 )
    maxDensity = round( np.max( densityScores ), 2 )
    
    metadataText = ( f"k: {k}\n"
                     f"Avg Density: {avgDensity}\n"
                     f"Min Density: {minDensity}\n"
                     f"Max Density: {maxDensity}" )

    # clusters & noise, top left
    fig.text( 0.02, 0.98,
              metadataText,
              fontsize=10,
              verticalalignment='top',
              bbox=dict( boxstyle="round,pad=0.3", edgecolor="black", facecolor="white" ) )

    # cluster color & num pts, top left (under previous)
    # legend = fig.legend( handles=legendEntries,
    #             loc="outside left upper",
    #             bbox_to_anchor=( 0, 0.84 ),
    #             title="Cluster Sizes",
    #             fontsize=10,
    #             title_fontsize=11 )
    # legend.get_frame().set_edgecolor("black")
    divider = make_axes_locatable( ax )
    cax = fig.add_axes( [0.08, 0.15, 0.03, 0.6] )
    cbar = fig.colorbar( scplt, cax=cax )
    # cbar = fig.colorbar( scplt, ax=ax, shrink=0.5, pad=0.15)
    cbar.ax.set_xlabel( 'kNN density', labelpad=10 )
    cbar.ax.xaxis.set_label_position( 'top' )
    

    if export:
        # ext = str(minPts) + "-" + str(e)
        filePath = "/scratch/sjc497/ADAPT/pngs/knn/"
        fig.savefig( filePath + str(astName) + "knn" + ".png" )
        plt.close()
    else:
        # doesn't work right now -- need to figure out what correct data to pass is.
        # cursor = mplcursors.cursor( hover=True )
        # cursor.connect( "add", lambda sel: sel.annotation.set_text( data[ "id" ].iloc[ sel.index ] ) )
        plt.show( block=True )
        fig.show()

