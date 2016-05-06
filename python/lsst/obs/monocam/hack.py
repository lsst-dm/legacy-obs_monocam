import os
import sqlite3
from lsst.pipe.base import Struct

from lsst.afw.coord import IcrsCoord
from lsst.afw.geom import Point2D, degrees
from lsst.afw.image import readMetadata, makeWcs

PIXELSCALE = 0.4  # arcsec/pixel

# XXX This is very naughty!
# We've got a bunch of data stuffed in a sqlite database that we want to use to stuff the registry.
# The database is a global (!) so we can get a hold of it from the depths.
_db = None
def getDatabase(root=None):
    global _db
    if _db is None:
        assert root is not None
        _db = sqlite3.connect(os.path.join(root, "monocam.sqlite"))
    return _db

def getHeader(filename):
    return readMetadata(filename, 1)  # 1 = PHU

def getDateFromHeader(md):
    return md.get("DATE-OBS")

def getShutterData(date):
    db = getDatabase()
    sql = """SELECT ra, decl, object, filter, type, expTime
    FROM shutter
    WHERE DATETIME(?) BETWEEN DATETIME(date, "-10 seconds") AND DATETIME(date, "+10 seconds");
    """
    cursor = db.cursor()
    cursor.execute(sql, [date])
    rows = cursor.fetchall()
    if len(rows) != 1:
        raise RuntimeError("Join with shutter metadata resulted in %d matches (%s --> %s)" %
                           (len(rows), date, sql))
    ra, dec, objectName, filterName, imageType, expTime = rows[0]
    return Struct(ra=ra, dec=dec, objectName=str(objectName), filterName=str(filterName),
                  imageType=str(imageType), expTime=expTime)

def fakeWcs(header):
    data = getShutterData(getDateFromHeader(header))
    return makeWcs(IcrsCoord(data.ra*degrees, data.dec*degrees), Point2D(2000, 2000),
                   PIXELSCALE/3600.0, 0.0, 0.0, PIXELSCALE/3600.0)
