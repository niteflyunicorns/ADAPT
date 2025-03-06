# python script to download specific FITS files from the ALeRCE database:
# ALeRCE database link: https://alerce.online/
# Savannah Chappus
# 10.22.2024

import os
import sys
import pandas as pd
from alerce.core import Alerce
import matplotlib.pyplot as plt
from astropy.io import fits
import numpy as np


urlPrefix = "https://avro.alerce.online/get_stamp?oid="
urlSpacer = "&candid="
urlSuffix = "&type=difference&format=fits"
inFolder = "/home/sjc497/astroInfoResearch/astroInfo/stamps/"
client = Alerce()


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
    for ztfID in data[ 'id' ]:
        hduList = client.get_stamps( ztfID )  # Returns an astropy.io.fits.HDUList
        # Loop through HDUs and save each stamp
        for hdu in hduList:
            if isinstance(hdu, fits.ImageHDU):  # Ensure it's an image
                data = hdu.data  # Extract pixel data

                if data is not None:  # Ensure there is valid data
                    # Normalize image for better visibility
                    norm_data = (data - np.min(data)) / (np.max(data) - np.min(data))

                    # Save as PNG
                    plt.imshow( norm_data, cmap="gray", origin="lower")
                    plt.axis("off")
                    plt.savefig( f"{ztfID}.png", bbox_inches="tight", pad_inches=0, dpi=150 )
                    plt.close()
    
def main():
    if len( sys.argv ) > 1:
        if ( sys.argv[ 1 ] == "True" ): # enter as "True"
            filePath = "/home/sjc497/astroInfoResearch/astroInfo/ztfIds.txt"
            fromFile( filePath )
    else:
        pass


main()
