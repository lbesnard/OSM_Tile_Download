#!/usr/bin/env python
import sys
from modules.osm import *

if __name__== '__main__':
    """
    Usage examples:
     ./osm_ogie3d.py example/2016-02-02-FLY-5348-01.IGC mount_wellington 15 outdoors | xargs display
     ./osm_ogie3d.py igcFile.igc testmap 11 sat
     ./osm_ogie3d.py igcFile.igc

    To be used in conjonction with OGIE3D and GPLIGC software for paragliding
    see http://pc12-c714.uibk.ac.at/GPLIGC/GPLIGC.html

    The script reads the LAT LON boundaries of an IGC file and  downloads tiles from openstreetmap
    using all different tile servers available, and doing it asynchronously to make it really fast

    The tiles are then merged into one jpg. The file is moved to the .gpligc/map folder if exists and the various information
    needed (map file path, corner coordinates) are added to the .ogierc config file for OGIE3D software.

    TODO:
     * many things ...
     * check server is online
     * async limitation of n of open files (see ulimit -n)
     * check user inputs
     * rename variables to be more understood
     * create optional arguments
     * what do to with ogierc has too many maps ?

    """

    if len(sys.argv) == 2:
        # default option values
        regionName = 'map'
        zoomLevel  = 15
        mapType    = 'outdoors'

    elif len(sys.argv) != 5 and len(sys.argv) > 2:
        sys.exit('Usage: osm_ogie3d.py igcFile.ig regionName(str) zoomLevel(1-18?) distance(km) mapType(sat landscape outdoors transport cycle)' % sys.argv[0])

    else:
         regionName  = str(sys.argv[2])
         zoomLevel   = int(sys.argv[3])
         mapType     = sys.argv[4]

    igcFilePath = sys.argv[1]

    maxLat, minLat, maxLon, minLon = getLatLonBoundariesIgc(igcFilePath)
    tilesDir                       = downloadOsmTiles(maxLat, minLat, maxLon, minLon, zoomLevel, mapType)
    aggregateMapPath               = aggregateTiles(tilesDir)
    mapOgiercPath                  = addMapOgiercConfig(aggregateMapPath, zoomLevel, regionName)
    print mapOgiercPath
    cleanFiles(tilesDir)
