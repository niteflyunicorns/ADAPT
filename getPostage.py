# python script to download specific FITS files from the ALeRCE database:
# ALeRCE database link: https://alerce.online/
# Savannah Chappus
# 10.22.2024

import os
import sys
import pandas as pd


urlPrefix = "https://avro.alerce.online/get_stamp?oid="
urlSpacer = "&candid="
urlSuffix = "&type=difference&format=fits"
inFolder = "/home/sjc497/astroInfoResearch/astroInfo/stamps/"


def readFile( filePath ):
    with open( filePath, 'r' ) as file:
        return file.readlines()

def fetchImage( url ):
    os.system( "wget --remote-encoding=utf-8 " + url )

def getURLS( filePath ):
    urls = list()
    for line in readFile( filePath ):
        fileName = line.strip()
        # print(fileName)
        ztfID, candID = line.split(', ')
        # print(ztfID)
        # print(candID)
        candID = candID.strip()
        newUrl = urlPrefix + ztfID + urlSpacer + candID + urlSuffix
        # print(newUrl)
        urls.append( newURL )
        
    return urls

def fromFile( filePath ):
    urls = getURLS( filePath )

    for url in urls:
        fetchImage( url )


def fromDF( data ): 
    for _, ztfID, candID, in data:
        

    
def main():
    if len( sys.argv ) > 1:
        if ( sys.argv[ 1 ] == "True" ) # enter as "True"
        filePath = "/home/sjc497/astroInfoResearch/astroInfo/ztfIds.txt"
        fromFile( filePath )
    else:
        pass


main()
