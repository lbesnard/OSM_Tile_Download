#!/usr/bin/env python
import sys, os
import shutil
from modules.osm import *

if __name__== '__main__':
    """
    This script downloads tiles from openstreetmap using all different tile servers available, and doing it asynchronously to make it really fast
    The tiles are then merged into one jpg.

    Usage examples:
     ./osm_download.py [map_name] [latitude_center] [longitude_center] [zoom_level] [distance_in_kms_from_lat_lon_center] [map_type(see below)] [output_dir]

     The map types allowed are : sat landscape outdoors transport cycle

     ./osm_download.py hobart -42.85 147.194824219 14 10 cycle /tmp | xargs display
     ./osm_download.py hobart -42.85 147.194824219 11 10 sat
     ./osm_download.py hobart -42.85 147.194824219 11 30 sat

    TODO:
     * many things ...
     * check server is online
     * async limitation of n of open files (see ulimit -n)
     * check user inputs
     * rename variables to be more understood
     * what do to with ogierc has too many maps ?

    """
    if len(sys.argv) != 8:
        sys.exit('Usage: osm_download.py regionName(str) latCenter lonCenter zoomLevel(1-18?) distance(km) mapType(sat landscape outdoors transport cycle) outputDir' % sys.argv[0])

    regionName = str(sys.argv[1])
    latCenter  = float(sys.argv[2])
    lonCenter  = float(sys.argv[3])
    zoomLevel  = int(sys.argv[4])
    distance   = float(sys.argv[5]) # in km
    mapType    = sys.argv[6]
    outputDir  = sys.argv[7]

    maxLat, minLat, maxLon, minLon = getBoundingBoxFromCenterPoint(lonCenter, latCenter, distance)
    tilesDir                       = downloadOsmTiles(maxLat, minLat, maxLon, minLon, zoomLevel, mapType)
    aggregateMapPath               = aggregateTiles(tilesDir)

    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    shutil.move(aggregateMapPath, os.path.join(outputDir, os.path.basename(aggregateMapPath)))
    cleanFiles(tilesDir)

    print os.path.join(outputDir, os.path.basename(aggregateMapPath))
