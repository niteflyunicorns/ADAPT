#########################################################################################
### Program: ADAPT (Anomaly Detection for Asteroid Patterns and Trends)
### Programmer: Savannah Chappus
### Last Update: 2.7.2025
###
### File: mongoConnection.py
### Use: handles logic for connecting to the mongo database for ZTF data
#########################################################################################

## IMPORTS ##############################################################################
from pymongo import MongoClient
import configparser as cfp


class Mongo:
    def __init__( self ):
        config = cfp.ConfigParser()
        config.read( 'config.ini' )
        user = config.get( 'Database', 'dbUser' )
        host = config.get( 'Database', 'dbHost' )
        port = config.get( 'Database', 'dbPort' )
        pswd = config.get( 'Database', 'dbPass' )

        dest = "mongodb://" + user + ":" + pswd + "@" + host + ":" + port
        client = MongoClient( dest )
        self.db = client.ztf

    def getData( self, dbKey ):
        newData = self.db[ dbKey ]
        return newData

# def getSecrets():
#     config = cfp.ConfigParser()
#     config.read( 'config.ini' )
#     user = config.get( 'Database', 'dbUser' )
#     host = config.get( 'Database', 'dbHost' )
#     port = config.get( 'Database', 'dbPort' )
#     pswd = config.get( 'Database', 'dbPass' )

#     return [ user, host, port, pswd ]


# def fetchDatabase():
#     user, host, port, pswd = getSecrets()
#     dest = "mongodb://" + user + ":" + pswd + "@" + host + ":" + port
#     client = MongoClient( dest )
#     db = client.ztf

#     return db


# def getData( ztfKey ):
#     db = fetchDatabase()
#     newData = db[ ztfKey ]
#     # mag18Data = db[ 'mag18o8' ] # all asteroids with mag18o8 data
#     # asteroidData = db[ 'asteroids_all' ]

#     return newData
