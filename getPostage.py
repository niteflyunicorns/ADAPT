# python script to download specific FITS files from the ALeRCE database:
# ALeRCE database link: https://alerce.online/
# Savannah Chappus
# 10.22.2024

### IMPORTS ######################################################################
import os
import sys
import pandas as pd
from alerce.core import Alerce
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.visualization import ZScaleInterval
import numpy as np

## Custom imports ##
from mongoConnection import Mongo


urlPrefix = "https://avro.alerce.online/get_stamp?oid="
urlSpacer = "&candid="
urlSuffix = "&type=difference&format=fits"
inFolder = "/home/sjc497/ADAPT/stamps/"
client = Alerce()


def readFile( filePath ):
    with open( filePath, 'r' ) as file:
        return [line.strip() for line in file]

def fetchImage( url ):
    try:
        os.system( "wget --remote-encoding=utf-8 " + url )
    except:
        print("Could not get ZTF image\n")

def getURLS( filePath ):
    urls = list()
    for line in readFile( filePath ):
        # fileName = line.strip()
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
    for ztfID in data[ 'id' ]:
        hduList = client.get_stamps( ztfID )  # Returns an astropy.io.fits.HDUList
        # Loop through HDUs and save each stamp
        for hdu in hduList:
            if isinstance(hdu, fits.ImageHDU):  # Ensure it's an image
                data = hdu.data  # Extract pixel data

                if data is not None:  # Ensure there is valid data
                    # Normalize image for better visibility
                    norm_data = (data - np.min(data)) / (np.max(data) - np.min(data))

                    norm_data = np.array( norm_data )

                    z = ZScaleInterval()
                    vmin, vmax = z.get_limits( data )
                    plt.imshow( data, origin='lower', cmap='gray', vmin=vmin, vmax=vmax )
                    # plt.colorbar()
                    # scale_data = z.__call__(norm_data, False)
                    # scale_data = ZScaleInterval.__call__( norm_data )
                    

                    # Save as PNG
                    # plt.imshow( scale_data, cmap="gray", origin="lower")
                    plt.axis("off")
                    plt.savefig( f"{ztfID}.png", bbox_inches="tight", pad_inches=0, dpi=150 )
                    plt.close()


# def fromMongo( astName, jd ):
    ## TODO: Do this later
    ## make mongo connection
    # db = Mongo.fetchDatabase( 'postageStamps' )
    # stamps = db[ 'availableObjects' ]
    # astStamps = stamps.find( {"ssnamenr": astName } )
    ## find imgs by string
    ## save them locally
    
    
def main():
    if len( sys.argv ) > 1:
        if ( sys.argv[ 1 ] == "True" ): # enter as "True"
            # filePath = "/home/sjc497/ADAPT/ztfIds.txt"
            filePath = "/scratch/sjc497/ADAPT/data/hybrid/ast6478ztfIds.txt"
            # fromFile( filePath )
            ztfIds = readFile( filePath )
            data = pd.DataFrame(ztfIds, columns=['id'])
            fromDF( data )

    else:
        pass

main()
