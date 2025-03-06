#########################################################################################
### Program: ADAPT (Anomaly Detection for Asteroid Patterns and Trends)
### Programmer: Savannah Chappus
### Last Update: 2.7.2025
###
### File: viewOneAst.py
### Use: handles logic for viewing data for one asteroid given via command line
#########################################################################################

### IMPORTS #############################################################################
import numpy as np
import pandas as pd

## Custom imports ##
import plotting as plot
import getObservations as getObs
import anomRatingADAPT as anomaly
import output as out


### VARIABLES ###########################################################################


#########################################################################################
### VIEWONE function
### Inputs: astArgs (name, feature to filter by, lower bound, upper bound), export flag
###         exportArgs(...), filter type, filter level, plots flag
### Returns: none
### Use: Allows user to specific the name ( numerical 'ssnamenr' from database ) of an
### asteroid they wish to analyze more in depth than in runProgram. 
#########################################################################################
def view( astData, astArgs, exportFlg, exportArgs, fltr, plots ):
    # note: currently, exportArgs is unused
    # process & repackage inputs
    astName = astArgs[ 0 ]
    featFltr = astArgs[ 1 ]
    lB = astArgs[ 2 ]
    uB = astArgs[ 3 ]
    data = pd.DataFrame( astData.mag18.find( { "ssnamenr": int( astName ) } ) )
    asteroid = astData.sort( data, "jd" )

    menu2Choice = 1 # hardcoded for testing purposes - move this to shell later!
    
    if menu2Choice == 1:
    # this is all for filter type 1 (anomaly rating) -- so this will have to wait until
    # I move that all to its own file
        print( "Asteroid " + str( astName ) + " Stats:\n" )
        print( astData.numFeatures )
        astSigmaMatrix = np.zeros( [ 1, astData.numFeatures + 2 ] )
        obsData = [ ]
        # filtering for anomaly rating.
        sigmaMatrix, obsData, astData.ztfIDS, outliers = anomaly.fillSigmaMatrix( astName, asteroid, astSigmaMatrix, fltr, True, plots, exportFlg )
        # post-processing for filter
        if len( sigmaMatrix ) == 0:
            # print( "ERROR: Your chosen filter level yielded an empty matrix!" )
            astData.ztfIDS.clear( )

        # print( astData.ztfIDS )
        print( sigmaMatrix )
        table = out.formatDataTable( sigmaMatrix, astData.ztfIDS, [ astName ], 1, astData.numFeatures )
        astRating = float( table[ "Rating" ] )

        # reset ztfIDS for reruns of program
        ### ERROR: This works for the most part, but still errors out upon quitting
        ### the program - not sure why
        astData.ztfIDS.clear( )

        # display filtered results
        print( table.transpose( ) )
        print( "\n\n" )

        displayAll = False # hardcoded for testing purposes - move this to shell later! 
        if ( displayAll ):
            print( "\n\n" )
            print( "Asteroid Rating: " + str( round( astRating, 2 ) ) + "%" )
            print( "\n" )

            for attr in astData.wantedAttrs:
                pass
                # TODO
                # add all attrs to little lists
                # add all little lists to a big list
                # convert to dataframe
                # df = pd.dataframe( data, columns=['sigma', 'outlier value', etc...] )
                # pass to out.screenDisplay( data, header )

            print( "ELONG:" )
            print( "    Sigma: ............. " + str( float( table[ "elong" ] ) ) )
            print( "    Outlier Value: ..... " + str( outliers[ 0 ] ) )
            print( "    Std Dev: ........... " + str( stat.stdev( asteroid[ "elong" ] ) ) )
            print( "    Mean: .............. " + str( stat.mean( asteroid[ "elong" ] ) ) )
            print( "    JD: ................ " + str( int( obsData[ 0 ] ) ) )
            print( "    ZTF ID: ............ " + str( astData.ztfIDS[ 0 ] ) )

            print( "RB:" )
            print( "    Sigma: ............. " + str( float( table[ "rb" ] ) ) )
            print( "    Outlier Value: ..... " + str( outliers[ 1 ] ) )
            print( "    Std Dev: ........... " + str( stat.stdev( asteroid[ "rb" ] ) ) )
            print( "    Mean: .............. " + str( stat.mean( asteroid[ "rb" ] ) ) )
            print( "    JD: ................ " + str( int( obsData[ 1 ] ) ) )
            print( "    ZTF ID: ............ " + str( astData.ztfIDS[ 1 ] ) )            

            print( "H:" )
            print( "    Sigma: ............. " + str( float( table[ "H" ] ) ) )
            print( "    Outlier Value: ..... " + str( outliers[ 2 ] ) )
            print( "    Std Dev: ........... " + str( stat.stdev( asteroid[ "H" ] ) ) )
            print( "    Mean: .............. " + str( stat.mean( asteroid[ "H" ] ) ) ) 
            print( "    JD: ................ " + str( int( obsData[ 2 ] ) ) )
            print( "    ZTF ID: ............ " + str( astData.ztfIDS[ 2 ] ) )            

            print( "MAG18:" )
            print( "    Sigma: ............. " + str( float( table[ "mag18omag8" ] ) ) )
            print( "    Outlier Value: ..... " + str( outliers[ 3 ] ) )
            print( "    Std Dev: ........... " + str( stat.stdev( asteroid[ "mag18omag8" ] ) ) )
            print( "    Mean: .............. " + str( stat.mean( asteroid[ "mag18omag8" ] ) ) )
            print( "    JD: ................ " + str( int( obsData[ 3 ] ) ) )
            print( "    ZTF ID: ............ " + str( astData.ztfIDS[ 3 ] ) )                            
            print( "\n\n" )
            print( asteroid[ [ "jd", "elong", "H", "rb", "mag18omag8", "fid" ] ] )



        ###### NEW PLOTTING ######
        if plots:
            plot.plot3Das2D( astName, asteroid['rb'],
                        asteroid['elong'],
                        asteroid['mag18omag8'],
                        "rb", "elong", "mag18omag8",
                        asteroid, exportFlg )

            plot.plot3Dand2D( astName, asteroid['rb'],
                        asteroid['elong'],
                        asteroid['mag18omag8'],
                        "rb", "elong", "mag18omag8",
                        asteroid, exportFlg )

        # call function to print all observations of
        # this asteroid
        getObs.getAll( astName, asteroid, astData.dataCols, exportFlg )

        # plot3D( astName, asteroid['rb'],
        #             asteroid['elong'],
        #             asteroid['mag18omag8'],
        #             "rb", "elong",
        #             "mag18omag8", exportFlg )


            
        # # setup for printing all plots later...
        # astDataFigs, ( ( plt3, plt2 ), ( plt1, plt4 ) ) = plt.subplots( 2, 2, figsize=( 15,15 ) )
        # astDataFigs.suptitle( "Asteroid " + str( astName ) )

        # # rb vs. Julian Date scatterplot
        # plt1.scatter( asteroid[ "jd" ], asteroid[ 'rb' ], color = 'deeppink' )
        # outlierRB = ( asteroid[ asteroid[ "rb" ] == outliers[ 1 ] ] ).index
        # plt1.scatter( asteroid[ "jd" ][ outlierRB ],
        #              asteroid[ "rb" ][ outlierRB ],
        #              color = 'white',
        #              marker = "." )
        # plt1.annotate( '%s' % obsData[ 1 ],
        #               xy = ( asteroid[ "jd" ][ outlierRB ],
        #                     asteroid[ "rb" ][ outlierRB ] ) )
        # plt1.set( xlabel = "jd", ylabel = "rb" )

        # # mag18omag8 vs. Julian Date scatterplot
        # plt2.scatter( asteroid[ "jd" ], asteroid[ 'mag18omag8' ], color = 'gold' )
        # outlierMAG18 = ( asteroid[ asteroid[ "mag18omag8" ] == outliers[ 3 ] ] ).index
        # plt2.scatter( asteroid[ "jd" ][ outlierMAG18 ],
        #              asteroid[ "mag18omag8" ][ outlierMAG18 ],
        #              color = 'white',
        #              marker = "." )
        # plt2.annotate( '%s' % obsData[ 3 ],
        #               xy = ( asteroid[ "jd" ][ outlierMAG18 ],
        #                     asteroid[ "mag18omag8" ][ outlierMAG18 ] ) )
        # plt2.set( xlabel = "jd", ylabel = "mag18omag8" )

        # # elong vs. Julian Date scatterplot
        # plt3.scatter( asteroid[ "jd" ], asteroid[ 'elong' ], color = 'blue' )
        # outlierELONG = ( asteroid[ asteroid[ "elong" ] == outliers[ 0 ] ] ).index
        # plt3.scatter( asteroid[ "jd" ][ outlierELONG ],
        #              asteroid[ "elong" ][ outlierELONG ],
        #              color = "white",
        #              marker = "." )
        # plt3.annotate( '%s' % obsData[ 0 ],
        #               xy = ( asteroid[ "jd" ][ outlierELONG ],
        #                     asteroid[ "elong" ][ outlierELONG ] ) )
        # plt3.set( xlabel = "jd", ylabel = "elong" )

        # # H vs. Julian Date scatterplot
        # # ERROR HERE!!!!!!!!!! - not showing up, may be reasoning for error in saving file
        # fidFiltered = asteroid.loc[ ( asteroid[ "fid" ] == 1 ) ]
        # # print(fidFiltered)
        # plt4.scatter( fidFiltered[ "jd" ], fidFiltered[ 'H' ], color = 'green' )
        # outlierH = ( asteroid[ asteroid[ "H" ] == outliers[ 2 ] ] ).index
        # # print(outlierH)
        # fidFiltered = asteroid.loc[ ( asteroid[ "fid" ] == 2 ) ]
        # # print(fidFiltered)
        # plt4.scatter( fidFiltered[ "jd" ], fidFiltered[ 'H' ], color = 'red' )
        # plt4.scatter( asteroid[ "jd" ][ outlierH ],
        #              asteroid[ "H" ][ outlierH ],
        #              color = "white",
        #              marker = "." )
        # plt4.annotate( '%s' % obsData[ 2 ],
        #               xy = ( asteroid[ "jd" ][ outlierH ],
        #                     asteroid[ "H" ][ outlierH ] ) )
        # plt4.set( xlabel = "jd", ylabel = "H" )

        
        # # if plots:
        # #     savefile = "ast" + str( astName ) + "-dataplots.png"
        # #     if exportFlg:
        # #         savefile = str( exportArgs[ 1 ] ) + "-dataplots.png"
                
        # #     astDataFigs.savefig( savefile )

        # ### TODO: add prompt for showing or exporting data
        # # astDataFigs.show( )

        # if ( plots ):
        #     astDataAllFigs, ( ( plt5, plt6, plt7 ),
        #                      ( plt8, plt9, plt10 ) ) = plt.subplots( 2, 3, figsize=( 15,15 ) )
        #     astDataAllFigs.suptitle( "Asteroid " + str( astName ) )

        #     # mag18omag8 vs. rb scatterplot
        #     plt5.scatter( asteroid[ "mag18omag8" ],
        #                  asteroid[ 'rb' ],
        #                  color = 'darkorange' )
        #     plt5.set( xlabel = "mag18omag8",
        #              ylabel = "rb",
        #              title = "mag18omag8 vs. rb" )

        #     # mag18omag8 vs. elong scatterplot
        #     plt6.scatter( asteroid[ "mag18omag8" ],
        #                  asteroid[ 'elong' ],
        #                  color = 'mediumaquamarine' )
        #     plt6.set( xlabel = "mag18omag8",
        #              ylabel = "elong",
        #              title = "mag18omag8 vs. elong" )

        #     # mag18omag8 vs. H scatterplot
        #     fidFiltered = asteroid.loc[ ( asteroid[ "fid" ] == 1 ) ]
        #     plt7.scatter( fidFiltered[ "mag18omag8" ],
        #                  fidFiltered[ 'H' ],
        #                  color = 'limegreen' )
        #     fidFiltered = asteroid.loc[ ( asteroid[ "fid" ] == 2 ) ]
        #     plt7.scatter( fidFiltered[ "mag18omag8" ],
        #                  fidFiltered[ 'H' ],
        #                  color = 'tomato' )
        #     plt7.set( xlabel = "mag18omag8",
        #              ylabel = "H",
        #              title = "mag18omag8 vs. H" )

        #     # rb vs. elong scatterplot
        #     plt8.scatter( asteroid[ "rb" ],
        #                  asteroid[ 'elong' ],
        #                  color = 'forestgreen' )
        #     plt8.set( xlabel = "rb",
        #              ylabel = "elong",
        #              title = "rb vs. elong" )

        #     # rb vs. H scatterplot
        #     fidFiltered = asteroid.loc[ ( asteroid[ "fid" ] == 1 ) ]
        #     plt9.scatter( fidFiltered[ "rb" ],
        #                  fidFiltered[ 'H' ],
        #                  color = 'darkgreen' )
        #     fidFiltered = asteroid.loc[ ( asteroid[ "fid" ] == 2 ) ]
        #     plt9.scatter( fidFiltered[ "rb" ],
        #                  fidFiltered[ 'H' ],
        #                  color = 'darkred' )
        #     plt9.set( xlabel = "rb",
        #              ylabel = "H",
        #              title = "rb vs. H" )

        #     # elong vs. H scatterplot
        #     fidFiltered = asteroid.loc[ ( asteroid[ "fid" ] == 1 ) ]
        #     plt10.scatter( fidFiltered[ "elong" ],
        #                   fidFiltered[ 'H' ],
        #                   color = 'seagreen' )
        #     fidFiltered = asteroid.loc[ ( asteroid[ "fid" ] == 2 ) ]
        #     plt10.scatter( fidFiltered[ "elong" ],
        #                   fidFiltered[ 'H' ],
        #                   color = 'firebrick' )
        #     plt10.set( xlabel = "elong",
        #               ylabel = "H",
        #               title = "elong vs. H" )

            # if ( input( "Export all plots as .png ( y/n )?" ) ):
            # if plots:
            #     savefileAll = "ast" + str( astName ) + "-alldataplots.png"
            #     if exportFlg:
            #         savefileAll = str( exportArgs[ 1 ] ) + "-alldataplots.png"

            #     astDataFigs.savefig( savefileAll )

            ### TODO: Add prompt for showing or exporting plots
            # when the above code is fixed, these two statements will be in the else for the exportFlg
            # plt.show(block=True)
            # astDataAllFigs.show( )

    elif menu2Choice == 2:
        print( "TODO: save data" )
    elif menu2Choice == 3:
        #filter by attribute
        attr = featFltr
        # if attr == 'l':
        #     print( attrList )
        #     attr = input( 
        #         "Attribute to filter by ( press 'l' for list of available attributes ): " )

        # attrData = input( "Desired attribute value: " )
        attrData = 0 # hardcoded - this part is kinda outdated too...

        # converting datatype as necessary
        if attr == "id":
            attrData = str( attrData )
        else:
            attrData = float( attrData )

        filteredData  = asteroid.loc[ ( asteroid[ attr ] == attrData ) ]

        print( filteredData[ [ "ssnamenr", "jd", "elong", "rb", "H", "mag18omag8", "id" ] ] )

        if attr == "jd":
            # print new plot with vertical line on plot for viewing one night specifically
            # astDataFigs.show( )
            jdAtObs = [ ]
            obsData = asteroid.loc[ ( asteroid[ attr ] == attrData ) ]
            for obs in range( len( obsData[ "jd" ] ) ):
                jdAtObs.append( float( obsData[ "jd" ].iloc[ obs ] ) )

            for obs in range( len( jdAtObs ) ):
                # rb line
                plt1.axvline( x = jdAtObs[ obs ], color = 'pink' )
                # mag18 line
                plt2.axvline( x = jdAtObs[ obs ], color = 'khaki' )
                # elong line
                plt3.axvline( x = jdAtObs[ obs ], color = 'skyblue' )
                # H line
                plt4.axvline( x = jdAtObs[ obs ], color = 'palegreen' )

            astDataFigs.show( )


    elif menu2Choice == 4:
        main( )
    else:
        pass


# TODO:
# translate remaining menu options into functions
# ie. view(), filter(), getObs(), plot(), getSpecificAttr()

def filter():
    pass



def preprocess( astData, astArgs, exportFlg, exportArgs, fltrType, fltrLvl, plots ):
    # note: currently, exportArgs is unused
    # process & repackage inputs
    astName = astArgs[ 0 ]
    featFltr = astArgs[ 1 ]
    lB = astArgs[ 2 ]
    uB = astArgs[ 3 ]
    fltr = [ fltrType, fltrLvl ]
    data = pd.DataFrame( astData.mag18.find( { "ssnamenr": int( astName ) } ) )
    asteroid = astData.sort( data, "jd" )
    astSigmaMatrix = np.zeros( [ 1, astData.numFeatures + 2 ] )
    obsData = [ ]
