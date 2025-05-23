#########################################################################################
### Program: ADAPT
### Programmer: Savannah Chappus
### Last Update: 2.3.2025
#########################################################################################

## IMPORTS ##############################################################################
import pandas as pd
import output as out
from tabulate import tabulate


# getAllObs: takes an asteroid and it's data and prints
# or exports each row in a nice neatly formatted way.
def getAll( name, data, cols, filepath, exportFlg ):
    header = "Asteroid " + str(name) + ": All Observations"
    tail = "\n"
    # for row in data:
    #     if row in [ "elong", "rb", "id", "night", "H", "mag18omag8" ]:
    #         miniDF = pd.concat( [ data[ "jd" ], data[ row ] ], axis=1, join='inner' )
    miniDF = data[ cols ]
    if not exportFlg:
        print( "Asteroid " + str( name ) + ":" )
        # print( str(row) )
        # print( str( data[ row ] ) )
        # print( miniDF )
        print( tabulate( miniDF, headers='keys', tablefmt='simple_outline' ) ) 
    else:
        filename = filepath + "ast" + str(name) + "_allObs"
        out.exportFile( 3, filename, miniDF )



def getSelect( name, obsToGet, data, cols, exportFlg ):
    header = "Asteroid " + str(name) + ": All Observations"
    tail = "\n"

    dropping = data.index.difference( obsToGet.index )
    df = data.drop( dropping )
        
    newDF = df[ cols ]
    if not exportFlg:
        print( "Asteroid " + str( name ) + ":" )
        print( tabulate( newDF, headers='keys', tablefmt='simple_outline' ) ) 
    else:
        pass
        # for now taking this out because otherwise hybrid outputs everything twice.
        # filename = filepath + "ast" + str(name) + "_selectObs"
        # out.exportFile( 3, filename, newDF )

    return df
