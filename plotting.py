#########################################################################################
### Program: ADAPT (Anomaly Detection for Asteroid Patterns and Trends)
### Programmer: Savannah Chappus
### Last Update: 1.29.2025
###
### File: plotting.py
### Use: plots specified data in 1D, 2D or 3D plots
#########################################################################################

### Imports #############################################################################
import matplotlib.pyplot as plt
import mplcursors
from matplotlib import gridspec


#########################################################################################
### Function: plot1D
### Inputs: asteroid name, data array, data name, and a flag for exporting
### Returns: none (either displays plot immediately, or silently exports to png)
#########################################################################################
def plot1D():
    pass

#########################################################################################
### Function: plot2D
### Inputs: asteroid name, x and y data arrays, x and y data names, and
###         a flag for exporting
### Returns: none (either displays plot immediately, or silently exports to png)
#########################################################################################
def plot2D( astName, xdata, ydata,
            data, xname, yname, export ):
    plt.title( "Asteroid " + str( astName ) )
    plt.scatter( xdata, ydata, color = 'deeppink' )
    plt.xlabel( xname )
    plt.ylabel( yname )

    if export:
        fig.savefig( str(astName) + "plots2D.png" )
    else:
        cursor = mplcursors.cursor( hover=True )
        cursor.connect( "add", lambda sel: sel.annotation.set_text( data[ "jd" ].iloc[ sel.index ] ) )
        plt.show( block = True )
        plt.show()


#########################################################################################
### Function: plot3D
### Inputs: asteroid name, x, y, and z data arrays, x, y, and z data names, and
###         a flag for exporting
### Returns: none (either displays plot immediately, or silently exports to png)
#########################################################################################
def plot3D( astName, xdata, ydata, zdata,
            xname, yname, zname, export ):
    
    # fig, ax = plt.subplots( projection='3d' )
    # fig.suptitle( "Asteroid " + str( astName ) )
    # ax.scatter( xdata, ydata, zdata,
    #             color = 'deeppink' )
    # ax.set_xlabel( xname )
    # ax.set_ylabel( yname )
    # ax.set_zlabel( zname )

    # if export:
    #     fig.savefig( str(astName) + "plot3D.png" )
    # else:
    #     plt.show( block=True )
    #     fig.show()

    pass
    
#########################################################################################
### Function: plot3Das2D
### Inputs: asteroid name, x, y, and z data arrays, x, y, and z data names, and
###         a flag for exporting
### Returns: none (either displays plot immediately, or silently exports to png)
#########################################################################################
def plot3Das2D( astName, xdata, ydata, zdata,
                    xname, yname, zname, data, export ):

    fig, ax = plt.subplots( 3, layout="constrained" )
    fig.suptitle( "Asteroid " + str( astName ) )

    # first subplot
    ax[0].scatter( xdata, ydata, color="deeppink" )
    ax[0].set_xlabel( xname )
    ax[0].set_ylabel( yname )

    # second subplot
    ax[1].scatter( xdata, zdata, color="slateblue" )
    ax[1].set_xlabel( xname )
    ax[1].set_ylabel( zname )

    # third subplot
    ax[2].scatter( zdata, ydata, color="teal" )
    ax[2].set_ylabel( yname )
    ax[2].set_xlabel( zname )


    if export:
        fig.savefig( str(astName) + "plots3-2D.png" )
    else:
        cursor = mplcursors.cursor( hover=True )
        cursor.connect( "add", lambda sel: sel.annotation.set_text( data[ "id" ].iloc[ sel.index ] ) )
        plt.show( block=True )
        # fig.show()
        
#########################################################################################
### Function: plot3Dand2D
### Inputs: asteroid name, x, y, and z data arrays, x, y, and z data names, and
###         a flag for exporting
### Returns: none (either displays plot immediately, or silently exports to png)
#########################################################################################
def plot3Dand2D( astName, xdata, ydata, zdata,
                    xname, yname, zname, data, export ):

    # export = False
    
    fig = plt.figure( figsize=(12, 8) )
    gs = gridspec.GridSpec( 1, 2, width_ratios=[ 1, 1.5 ] )
    fig.suptitle( "Asteroid " + str( astName ) )


    ax3d = fig.add_subplot( gs[0,0], projection='3d' )
    ax3d.scatter( xdata, ydata, zdata,
                  color = 'darkorchid' )
    ax3d.set_xlabel( xname )
    ax3d.set_ylabel( yname )
    ax3d.set_zlabel( zname )

    gs_right = gridspec.GridSpecFromSubplotSpec( 3, 1, subplot_spec=gs[0,1],
                                        height_ratios=[1, 1, 1], hspace=0.4 )

    ax2d1 = fig.add_subplot( gs_right[0] )
    ax2d2 = fig.add_subplot( gs_right[1] )
    ax2d3 = fig.add_subplot( gs_right[2] )

    gs.update( wspace=0.4, hspace=0.4 )

    ax2d1.scatter( xdata, ydata, color = 'deeppink' )
    ax2d1.set_xlabel( xname )
    ax2d1.set_ylabel( yname )

    ax2d2.scatter( xdata, zdata, color = 'slateblue' )
    ax2d2.set_xlabel( xname )
    ax2d2.set_ylabel( zname )

    ax2d3.scatter( zdata, ydata, color = 'teal' )
    ax2d3.set_xlabel( zname )
    ax2d3.set_ylabel( yname )

    if export:
        fig.savefig( str(astName) + "plots3D+2D.png" )
    else:
        cursor = mplcursors.cursor( hover=True )
        cursor.connect( "add", lambda sel: sel.annotation.set_text( data[ "id" ].iloc[ sel.index ] ) )
        plt.show( block=True )
        fig.show()
