#########################################################################################
### Program: ADAPT (Anomaly Detection for Asteroid Patterns and Trends)
### Programmer: Savannah Chappus
### Last Update: 4.3.2025
###
### File: hybridADAPT.py
### Use: handles mixing DBSCAN and IsolationForest filtering on asteroid data
#########################################################################################

## IMPORTS ##############################################################################
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import Normalizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
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

## Global Variables ##
feats = [ "elong", "rb", "mag18omag8" ]
colors = { "light": [ "lightcoral", "bisque","khaki",
                      "darkseagreen", "lightgreen",
                      "aquamarine", "aqua",
                      "lightblue", "cornflowerblue",
                      "mediumpurple", "thistle", "pink" ],
           "dark": [ "maroon", "darkorange", "gold",
                     "darkgreen", "seagreen",
                     "darkslategray", "teal",
                     "steelblue", "darkblue", 
                     "indigo", "darkmagenta", "deeppink" ],
           "noise": [ "gray", "black" ] }


def float_range( start, stop, step, precision=2 ):
    while start < stop:
        yield round( start, precision )
        start += step

def preProcess( astData, name, process ):
    data = pd.DataFrame( astData.mag18.find( { "ssnamenr": int( name ) } ) )
    sortedDF = astData.sort( data, "jd" )
    df = astData.trimToCols( sortedDF, feats )
    dataArray = df.to_numpy()
    if process == 'db':
        scaler = Normalizer()
        normData = scaler.fit_transform( dataArray )
        return sortedDF, dataArray, normData
    else:
        trainData, testData  = train_test_split( dataArray, random_state=42 )
        return sortedDF, trainData, testData

def plotDBSCAN( ax, labels, db, extras, data, astName, export ):
    minPts, e, clusterSizes = extras
    unique_labels = set(labels)
    core_samples_mask = np.zeros_like(labels, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    legendEntries = []

    n_clusters_ = len( set( labels ) ) - ( 1 if -1 in labels else 0 )
    n_noise_ = list( labels ).count( -1 )

    # colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
    for k, col in zip(unique_labels, colors[ "light" ]):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]

        class_member_mask = labels == k

        xyz = data[class_member_mask & core_samples_mask]
        ax.scatter(
            xyz[:, 0],
            xyz[:, 1],
            xyz[:, 2],
            color=col,
            edgecolors="k",
            s=100,
        )

        xyz = data[class_member_mask & ~core_samples_mask]
        ax.scatter(
            xyz[:, 0],
            xyz[:, 1],
            xyz[:, 2],
            color=col,
            edgecolors="k",
            s=40,
        )

        # formatting for color/numPts legend
        clusterSize = np.sum( labels == k )
        labelText = f"{clusterSize} pts"
        patch = mpatches.Patch( color=col, label=labelText )
        if len( legendEntries ) <= 15:
            legendEntries.append( patch )

    noisePercent = ( n_noise_ / len( labels ) ) * 100
    metadataText = ( f"Clusters: {n_clusters_}\n"
                     f"Noise: {noisePercent:.2f}%\n"
                     f"MinPts: {minPts}\n"
                     f"Epsilon: {e}" )

    return metadataText, legendEntries

   

def plotISO( ax, data, astName, export ):
    normal = data[ data[ 'anomaly' ] == 1 ]
    anomalies = data[ data[ 'anomaly' ] == -1 ]

    ax.scatter( normal[ "elong" ],
                normal[ "rb" ],
                normal[ "mag18omag8" ],
                label='Normal',
                color=colors[ "light" ][ 0 ],
                edgecolors="k", s=100 )
    ax.scatter( anomalies[ "elong" ],
                anomalies[ "rb" ],
                anomalies[ "mag18omag8" ],
                label='Anomaly',
                color=colors[ "noise" ][ 1 ],
                edgecolors="k", s=40 )

    anomRate = ( len( anomalies ) / len( data ) ) * 100
    metadataText = ( f"Anomaly Rate: {anomRate:.2f}%" )

    return metadataText
    

def plotMIX( ax, labels, db, extras, data, isoResults, astName, export ):
    minPts, e, clusterSizes = extras
    unique_labels = set(labels)
    core_samples_mask = np.zeros_like(labels, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    legendEntries, legendEntries2 = [], []

    n_clusters_ = len( set( labels ) ) - ( 1 if -1 in labels else 0 )
    n_noise_ = list( labels ).count( -1 )
    clustColors = colors[ "light" ]
    anomColors = colors[ "dark" ]
    # combinedLabels = np.where( ( labels == -1 ) & ( isoResults == -1 ), -2, labels )

    for k in set( labels ):
        if k == -1:
            col = colors[ "noise" ][ 0 ]
            anomCol = colors[ "noise" ][ 1 ]
        else:
            col = clustColors[ k ]
            anomCol = anomColors[ k ]

        class_member_mask = labels == k
        anomaly_mask = isoResults == -1

        # core normal
        xyz = data[class_member_mask & core_samples_mask & ~anomaly_mask]
        ax.scatter(
            xyz[:, 0],
            xyz[:, 1],
            xyz[:, 2],
            c=col,
            edgecolors="k",
            s=100,
        )

        # core anomaly
        xyz = data[class_member_mask & core_samples_mask & anomaly_mask]
        ax.scatter(
            xyz[:, 0],
            xyz[:, 1],
            xyz[:, 2],
            c=anomCol,
            edgecolors="k",
            s=100,
        )

        # border normal
        xyz = data[class_member_mask & ~core_samples_mask & ~anomaly_mask]
        ax.scatter(
            xyz[:, 0],
            xyz[:, 1],
            xyz[:, 2],
            c=col,
            edgecolors="k",
            s=40,
        )

        # border anomaly
        xyz = data[class_member_mask & (~core_samples_mask) & anomaly_mask]
        ax.scatter(
            xyz[:, 0],
            xyz[:, 1],
            xyz[:, 2],
            c=anomCol,
            edgecolors="k",
            s=40,
        )


        # formatting for color/numPts legend
        clusterSize = np.sum( class_member_mask & ~anomaly_mask )
        labelText = f"{clusterSize} pts"
        patch = mpatches.Patch( color=col, label=labelText )
        if len( legendEntries ) <= 15:
            legendEntries.append( patch )
            
        anomClustSize = np.sum( class_member_mask & anomaly_mask )
        labelText2 = f"{anomClustSize} pts"
        patch2 = mpatches.Patch( color=anomCol, label=labelText2 )
        if len( legendEntries2 ) <= 15:
            legendEntries2.append( patch2 )


    return legendEntries, legendEntries2

    
def run( astData, plots, export ):
    names = astData.names
    for astName in names:
        ###############################################################################
        ### ISOLATION FOREST CODE ###
        ### run isolation forest and get outliers
        untrimmed, trainData, testData = preProcess( astData, astName, 'iso' )
        features = untrimmed[ feats ]

        state = 0 # starting point
        samples = 100 # starting point

        tune = False
        stamps = False
        if tune:
            paramTune( astData, astName, plots, export )
        else:
            clf = IsolationForest( max_samples=samples, random_state=state )
            clf.fit( trainData )
            trimmed = untrimmed.loc[ features.index ].copy()
            trimmed[ 'anomalyScore' ] = clf.decision_function( features )
            trimmed[ 'anomaly' ] = clf.predict( features )
            isoResults = trimmed[ 'anomaly' ]

            # if ( plots ):
            #     plotIForest( trimmed, astName, export )

            # if ( export ):
            #     pass
            #     # out.exportFile( 3, str(astName) + "clusterData", clusterData )
            # else:
            #     pass
            #     # out.screenDisplay( clusterData, "Cluster Data" )

            # if ( stamps ):
            #     postage.fromDF( clusterData )


        ###############################################################################
        ### DBSCAN CODE ###
        ### run dbscan and get clusters
        untrimmed, unnorm, data = preProcess( astData, astName, 'db' )

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
                # plotDBSCAN( labels, db, extraStuff, unnorm, astName, export )

            # clusterData = fetchDataForCluster( 1, untrimmed, labels, astName, astData.dataCols, export )

            getObs.getAll( astName, untrimmed, astData.dataCols, export )
            # if ( export ):
            #     out.exportFile( 3, str(astName) + "clusterData", clusterData )
            # else:
            #     out.screenDisplay( clusterData, "Cluster Data" )

            # if ( stamps ):
            #     postage.fromDF( clusterData )


        ###############################################################################
        ### HYBRID CODE ###
        ### filter the iso and dbscan results as follows:
        ### High anomaly (or artifact): noise in DBSCAN and anomaly in IsoForest
        ### Med anomaly: cluster in DBSCAN but anomaly in IsoForest
        ### Low anomaly: anomalies in IsoForest that are in big clusters in DBSCAN
        ### No anomaly?: big clusters in DBSCAN or normal rankings in IsoForest


        if plots:
            # setup
            fig = plt.figure( figsize=(12, 6.75)  )
            axs = [ fig.add_subplot( 1, 3, i + 1, projection="3d" ) for i in range(3) ]
            plt.subplots_adjust( bottom = 0.3,
                                 right = 0.95,
                                 left = 0,
                                 wspace = 0.15 )


            # plot 3 subplots
            dbMetadataTxt, dbLegEntries = plotDBSCAN(axs[0], labels, db, extraStuff, unnorm, astName, export )
            isoMetadataTxt = plotISO(axs[1], trimmed, astName, export )
            mixLegEntries, mixLegEntries2 = plotMIX(axs[2], labels, db, extraStuff, unnorm, isoResults, astName, export )

            # tuning plots and adding legends
            fig.suptitle( f"Asteroid {astName}", fontsize=20 )
            for ax in axs:
                    ax.set_xlabel( "elong" )    
                    ax.set_ylabel( "rb" )
                    ax.set_zlabel( "mag18omag8" )
                    ax.set_xlim(np.min(unnorm[:, 0]), np.max(unnorm[:, 0]))
                    ax.set_ylim(np.min(unnorm[:, 1]), np.max(unnorm[:, 1]))
                    ax.set_zlim(np.min(unnorm[:, 2]), np.max(unnorm[:, 2]))



            # LEGENDS ####################

            ## DBSCAN LEGENDS ############
            # clusters & noise, top left
            fig.text( 0.007, 0.98,
                      dbMetadataTxt,
                      fontsize=10,
                      verticalalignment='top',
                      bbox=dict( boxstyle="round,pad=0.3", edgecolor="black", facecolor="white" ) )

            # cluster color & num pts, top left (under previous)
            dbLegend = fig.legend( handles=dbLegEntries,
                        loc="outside left lower",
                        bbox_to_anchor=( 0, 0 ),
                        title="Cluster Sizes",
                        fontsize=10,
                        title_fontsize=11 )
            dbLegend.get_frame().set_edgecolor("black")


            ## ISO LEGENDS ###############
            fig.text( 0.5, 0.05,
                      isoMetadataTxt,
                      fontsize=10,
                      verticalalignment='top',
                      horizontalalignment='center',
                      bbox=dict( boxstyle="round,pad=0.3", edgecolor="black", facecolor="white" ) )
            
            isoLegend = fig.legend( loc="outside upper center",
                        bbox_to_anchor=( 0.5, 0.15 ) )
            isoLegend.get_frame().set_edgecolor("black")

            ## MIX LEGENDS ###############
            # cluster color & num pts, top left (under previous)
            mixLegend1 = fig.legend( handles=mixLegEntries,
                        loc="outside right lower",
                        bbox_to_anchor=( 1, 0 ),
                        title="Normal Clusters",
                        fontsize=10,
                        title_fontsize=11 )
            mixLegend1.get_frame().set_edgecolor("black")

            mixLegend2 = fig.legend( handles=mixLegEntries2,
                        loc="outside right lower",
                        bbox_to_anchor=( 0.88, 0 ),
                        title="Iso Anomalies",
                        fontsize=10,
                        title_fontsize=11 )
            mixLegend2.get_frame().set_edgecolor("black")

            fig.set_dpi(300)

            if export:
                ext = "(" + str(minPts) + "-" + str(e) + ")"
                filePath = "/home/sjc497/ADAPT/pngs/hybrid/"
                fig.savefig( filePath + str(astName) + "hybrid" + ext + ".png" )
                plt.close()
            else:
                plt.show( block=True )
                fig.show()

