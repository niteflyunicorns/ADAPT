#########################################################################################
### Program: ADAPT (Anomaly Detection for Asteroid Patterns and Trends)
### Programmer: Savannah Chappus
### Last Update: 2.14.2025
###
### File: processing.py
### Use: handles logic for processing data before filtering, viewing, etc.
#########################################################################################

### IMPORTS #############################################################################
import pandas as pd

## Custom imports ##
from mongoConnection import Mongo


# internal variables
mongo = Mongo()
asteroidData = mongo.getData( 'asteroids_all' )


# AstData Class for holding all commonly used variables
class AstData():
    def __init__( self ):
        self.mag18 = mongo.getData( 'mag18o8' )
        self.wantedAttrs = list()
        self.dataCols = list()
        self.numFeatures = 0
        self.offset = 0
        self.maxIn = 0
        self.ztfIDS = list()
        self.weightDict = {} # currently unused
        self.names = pd.DataFrame()


    def setupAttrs( self, attrs, extras ):
        self.wantedAttrs = attrs.copy()
        self.dataCols = attrs.copy()
        self.dataCols.extend( extras )
        self.numFeatures = len( attrs )

    def setAstNames( self ):
        self.names = pd.DataFrame( asteroidData.find( {},{ '_id': 0, 'ssnamenr': 1 } ) )

    def setOffset( self, value=-1 ):
        if ( value < 0 and maxIn < asteroidData.count() ):
            self.offset = rand.randint( 0, asteroidData.count() - maxIn - 1 )
        else:
            self.offset = value

    def setMaxIn( self, value=-1 ):
        if value < 0:
            self.maxIn = self.names.size
        else:
            self.maxIn = value
            
    def sort( self, data, sortBy ):
        return data.sort_values( by = [ sortBy ] )

    def trimToCols( self, data, cols ):
        return data[ cols ]
    
    def findAst( self, name ):
        return pd.DataFrame( self.mag18.find( { "ssnamenr": int( name ) } ) )
        
