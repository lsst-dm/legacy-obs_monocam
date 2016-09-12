from builtins import str
import os
import sqlite3
from lsst.pipe.base import Struct

from lsst.afw.coord import IcrsCoord
from lsst.afw.geom import Point2D, degrees
from lsst.afw.image import readMetadata, makeWcs

"""
This module contains hacks for getting information from the monocam data when it's in use at USNO.

The monocam controllers don't (can't?) talk to the telescope, and so the usual telescope header keywords
(e.g., RA, DEC, OBJECT, EXPTIME, FILTER) are not included in the FITS headers. Instead, separate FITS files
are written treating the shutter as an instrument. In order to operate as normal, we need to correlate the
camera files with the shutter files. We do this by ingesting the useful data from the shutter files into
a SQLite database, and then querying this database whenever we need data for a camera file, using the date
to correlate the two. Unfortunately, the dates aren't exact because the clocks of the two systems aren't
synchronised and the events in the two systems have different delays. A 10 second window does a decent job
of correlating the two, but could get confused if multiple exposures are taken with short delays.

This is an awful hack (e.g., requires a global/singleton for the database handle). It's not clear whether
this hack will be needed for future observations, or if it's only required to process a few nights' worth of
observations.
"""


PIXELSCALE = 0.4  # arcsec/pixel; according to Dave Monet
WINDOW = "10 seconds"  # Time window for matching with the database

_db = None  # Database handle singleton


def getDatabase(root=None):
    """Provide a database handle

    The first call of this function requires the root directory, where the SQLite
    database is located. We cache the handle and provide it on subsequent calls.
    The database handle is effectively a singleton, which is very naughty (!!!), but
    we need to get a hold of it from the depths of different functions that weren't
    designed to pass extra information to and fro. In a real production system,
    this shouldn't be required.
    """
    global _db
    if _db is None:
        assert root is not None
        _db = sqlite3.connect(os.path.join(root, "monocam.sqlite"))
    return _db


def getHeader(filename):
    """Get the primary header

    Monocam data is written with all the useful stuff in the PHU, but not using
    "INHERIT = T" in the subsequent HDUs so that reading those HDUs doesn't provide
    any useful data.
    """
    return readMetadata(filename, 1)  # 1 = PHU


def getDateFromHeader(md):
    return md.get("DATE-OBS")


def getShutterData(date):
    """Find shutter data in our database that matches a particular date

    Returns a Struct with ra, dec, objectName, filterName, imageType, expTime.
    """
    db = getDatabase()
    sql = """SELECT ra, decl, object, filter, type, expTime
    FROM shutter
    WHERE DATETIME(?) BETWEEN DATETIME(date, "-%s") AND DATETIME(date, "+%s");
    """ % (WINDOW, WINDOW)
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
    """Generate a fake Wcs given a camera header

    The intent of the fake Wcs is not so much to be accurate (we have no information
    on the rotator angle, and who knows if we've got the parity correct), but to be
    close enough so that astrometry.net can find a solution. That means having the
    RA,Dec close-ish, and the pixel scale about right or slightly over-estimated.
    """
    data = getShutterData(getDateFromHeader(header))
    return makeWcs(IcrsCoord(data.ra*degrees, data.dec*degrees), Point2D(2000, 2000),
                   PIXELSCALE/3600.0, 0.0, 0.0, PIXELSCALE/3600.0)
