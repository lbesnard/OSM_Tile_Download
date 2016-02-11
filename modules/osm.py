#!/usr/bin/env python

import sys, os
import subprocess
import itertools
import shutil
import math
import random
import tempfile
from modules.IGC2CSV import *

def getTileRange(maxLat, minLat, maxLon, minLon, zoomLevel):
    northWestTileNumber = deg2num(maxLat, minLon, zoomLevel)
    southEastTileNumber = deg2num(minLat, maxLon, zoomLevel)
    xTileRange          = range(northWestTileNumber[0], southEastTileNumber[0])
    yTileRange          = range(northWestTileNumber[1], southEastTileNumber[1])
    tileRange           = list(itertools.product(xTileRange, yTileRange))
    return tileRange

def generateUrlsRandomServer(tileRange, zoomLevel, mapType):
    # we create urls with random servers not to overload the servers, and to download faster
    # SAT image : otile1 to otile4 'http://otile{s}.mqcdn.com/tiles/1.0.0/sat/{z}/{x}/{y}.png'
    # various maps servers a. b. c. ... http://b.tile.thunderforest.com/cycle/15/29785/20721.png
    mapTypeAvailable = ['sat', 'landscape', 'outdoors', ' transport', 'cycle']

    if mapType == 'sat':
        servValues = ['otile1', 'otile2', 'otile3', 'otile4']
        servUrl    = 'mqcdn.com/tiles/1.0.0'
    else:
        servValues = ['a', 'b', 'c']
        servUrl    = 'tile.thunderforest.com'

    url       = []
    imagePath = []
    for tileCouple in tileRange:
        randomServValue = random.choice(servValues)
        imagePath.append('%s/%s.png' % (tileCouple[0], tileCouple[1]))
        url.append('http://%s.%s/%s/%s/%s/%s.png' % (str(randomServValue), servUrl, mapType, zoomLevel, tileCouple[0], tileCouple[1]))

    return url, imagePath

def downloadAsync(urlList, outputFilePathList):
    """ warning if n files too big to download at once, ie than 1024 by default, this will break.
    need to improve this function by calling ulimit -n and sub seeting the urlList
    """
    # http://stackoverflow.com/questions/18377475/asynchronously-get-and-store-images-in-python
    import grequests
    requests = (grequests.get(u) for u in urlList)
    responses = grequests.map(requests)
    i = 0
    for response in responses:
        if 199 < response.status_code < 400:
            name = outputFilePathList[i]
            with open(name, 'wb') as f:
                f.write(response.content)
        i+=1

def downloadOsmTiles(maxLat, minLat, maxLon, minLon, zoomLevel, mapType):
    tileRange              = getTileRange(maxLat, minLat, maxLon, minLon, zoomLevel)
    urlList, imagePathList = generateUrlsRandomServer(tileRange, zoomLevel, mapType)

    imageFolderName        = tempfile.mkdtemp()
    imageFullPathList      = [ os.path.join(imageFolderName, s) for s in imagePathList]

    # create the dir, subdirs where the images will be downloaded
    for dir in imageFullPathList:
        dir = os.path.dirname(dir)
        if not os.path.exists(dir):
            os.makedirs(dir)
    downloadAsync(urlList, imageFullPathList)
    return imageFolderName

def deg2num(lat_deg, lon_deg, zoomLevel):
    """ http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
    Lon./lat. to tile numbers
    Tile numbers to lon./lat.
    """
    lat_rad = math.radians(lat_deg)
    n       = 2.0 ** zoomLevel
    xtile   = int((lon_deg + 180.0) / 360.0 * n)
    ytile   = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return xtile, ytile

def num2deg(xtile, ytile, zoomLevel):
    n       = 2.0 ** zoomLevel
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg

def listTilesDir(tilesDir):
    vertTileDir = [ vertTileDir for vertTileDir in os.listdir(tilesDir) if os.path.isdir(os.path.join(tilesDir, vertTileDir)) ]
    vertTileDir.sort()
    return tilesDir, vertTileDir

def aggregateTiles(tilesDir):
    import glob
    tileDir, vertTileDir = listTilesDir(tilesDir)
    for vertTile in vertTileDir:
        a                  = [ os.path.join(tileDir, vertTile, image) for image in os.listdir(os.path.join(tileDir, vertTile))]
        a.sort()
        argImageMagicklist = [['convert', '-append'], a, [os.path.join(tileDir, '%s_vert.png' % vertTile)]]
        chain              = itertools.chain(*argImageMagicklist)
        subprocess.call(list(chain))

    vertAggregateImages = glob.glob(os.path.join(tileDir,'*_vert.png'))
    vertAggregateImages.sort()
    aggregateMapPath    = [os.path.join(tilesDir, 'map.jpg')]
    argImageMagicklist  = [['convert', '+append'], vertAggregateImages, aggregateMapPath]
    chain               = itertools.chain(*argImageMagicklist)
    subprocess.call(list(chain))

    return aggregateMapPath[0]

def hashMd5Gen():
    import random
    hash = random.getrandbits(128)
    return ("%032x" % hash)[0:5]

def locationDistanceBearing(lon, lat, d, brng):
    import geopy
    from geopy.distance import VincentyDistance
    # given: lat1, lon1, b = bearing in degrees, d = distance in kilometers
    origin = geopy.Point(lat, lon)
    destination = VincentyDistance(kilometers=d).destination(origin, brng)
    return destination[1], destination[0]

def getBoundingBoxFromCenterPoint(lon, lat, d):
    """ given the center point location, and a distance, return the bounding box coordinates"""
    [lonT, latT] = locationDistanceBearing(lon, lat, d, 0)
    [lonR, latR] = locationDistanceBearing(lon, lat, d, 90)
    [lonB, latB] = locationDistanceBearing(lon, lat, d, 180)
    [lonL, latL] = locationDistanceBearing(lon, lat, d, 260)
    maxLat = latT
    minLat = latB
    maxLon = lonR
    minLon = lonL
    return maxLat, minLat, maxLon, minLon

def cleanFiles(tilesDir):
    mapTmpDir = os.path.join(os.environ['HOME'], tilesDir)
    if os.path.isdir(mapTmpDir):
        shutil.rmtree(mapTmpDir)

##############################
# OGIE 3D functions specific #
##############################
def getTilesLatLonExtent(tilesDir, zoomLevel):
    import math
    tileDir, vertTileDir = listTilesDir(tilesDir)

    firtImageXCoord      = float(vertTileDir[0])
    lastImageXCoord      = float(vertTileDir[-1])
    firstImageYCoord     = [image for image in os.listdir(os.path.join(tileDir, vertTileDir[0]))]
    firstImageYCoord.sort()
    firstImageYCoord     = float(os.path.splitext(firstImageYCoord[0])[0])

    lastImageYCoord      = [image for image in os.listdir(os.path.join(tileDir, vertTileDir[-1]))]
    lastImageYCoord.sort()
    lastImageYCoord      = float(os.path.splitext(lastImageYCoord[-1])[0])

    northWestCorner      = num2deg(firtImageXCoord,firstImageYCoord, zoomLevel)
    southEastCorner      = num2deg(lastImageXCoord +1 , lastImageYCoord +1, zoomLevel)

    return northWestCorner, southEastCorner

def addMapOgiercConfig(aggregateMapPath, zoomLevel, regionName):
    tilesDir                           = os.path.dirname(aggregateMapPath)
    [northWestCorner, southEastCorner] = getTilesLatLonExtent(tilesDir, zoomLevel)
    ogiercConfigFilePath               = os.path.join(os.environ['HOME'], '.ogierc')

    if os.path.isfile(ogiercConfigFilePath):
        # copy file to gpligc map folder
        gpligcMapDir = os.path.join(os.environ['HOME'], '.gpligc', 'map')
        if not os.path.isdir(gpligcMapDir):
            os.makedirs(gpligcMapDir)

        # create a hash value to append at the end of the map filename so we don't have duplicate
        hashValue              = hashMd5Gen()
        aggregateMapGpligcPath = os.path.join(gpligcMapDir, 'map_%s_%s.jpg' % (regionName, hashValue))

        shutil.move(aggregateMapPath, aggregateMapGpligcPath)

        with open(ogiercConfigFilePath, "a") as myfile:
                myfile.write('\nMAP_FILE %s\n'   % aggregateMapGpligcPath)
                myfile.write('MAP_TOP %s\n'    % northWestCorner[0])
                myfile.write('MAP_BOTTOM %s\n' % southEastCorner[0])
                myfile.write('MAP_LEFT %s\n'   % northWestCorner[1])
                myfile.write('MAP_RIGHT %s\n\n'  % southEastCorner[1])
        return aggregateMapGpligcPath

    return []

def getLatLonBoundariesIgc(igcFilePath):
    logbook = []
    logbook.append({'igcfile': os.path.abspath(igcFilePath)})

    # prevent external function from printing in the batch console
    sys.stdout = open(os.devnull, "w")
    for flight in logbook:
        flight = parse_igc(flight)
        flight = crunch_flight(flight)
    sys.stdout = sys.__stdout__

    lon = []
    lat = []
    for iRecord in range(len(flight['fixrecords'])):
        lat.append(flight['fixrecords'][iRecord]['latdegrees'])
        lon.append(flight['fixrecords'][iRecord]['londegrees'])

    # add 2-3 kms to sides , roughly 0.027 deg
    addOffset = 0.027

    return max(lat) + addOffset, min(lat) - addOffset, max(lon) + addOffset, min(lon) - addOffset
