import os
import re
from lsst.afw.image import readMetadata, makeWcs, DecoratedImageU
from lsst.afw.coord import IcrsCoord
from lsst.afw.geom import Point2D, degrees
from lsst.pipe.base import Struct
from lsst.pipe.tasks.ingest import IngestTask, ParseTask, RegisterTask, assertCanCopy
from lsst.pipe.tasks.ingestCalibs import CalibsParseTask

# XXX This is completely made up
filters = {
    0: 'u',
    1: 'g',
    2: 'r',
    3: 'i',
    4: 'z',
    5: 'y',
    "UNK": "UNKNOWN",
}

EXTENSIONS = ["fits", "gz", "fz"]
PIXELSCALE = 0.4  # arcsec/pixel

# XXX This is very naughty!
# We've got a bunch of data stuffed in a sqlite database that we want to use to stuff the registry.
# The database is a global (!) so we can get a hold of it from the depths.
_db = None
def getDatabase(root=None):
    global _db
    if _db is None:
        assert root is not None
        import sqlite3
        _db = sqlite3.connect(os.path.join(root, "monocam.sqlite"))
    return _db

def joinShutter(date):
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


class HackParseTask(ParseTask):
    _counter = -1  # Visit counter; negative so it doesn't overlap with the 'id' field, which autoincrements

    def getInfo(self, filename):
        md = readMetadata(filename, 1)
        data = joinShutter(md.get("DATE-OBS"))
        visit = self._counter
        self._counter -= 1
        basename = os.path.basename(filename)
        while any(basename.endswith("." + ext) for ext in EXTENSIONS):
            basename = basename[:basename.rfind('.')]
        info = {"visit": visit,
                "filter": data.filterName,
                "basename": basename,
                "date": md.get("DATE-OBS"),
                "expTime": data.expTime,
                "ccd": 0,
                "object": data.objectName,
        }
        return info, [info]


class MonocamParseTask(ParseTask):
    _counter = -1  # Visit counter; negative so it doesn't overlap with the 'id' field, which autoincrements

    def getInfo(self, filename):
        # Grab the basename
        phuInfo, infoList = ParseTask.getInfo(self, filename)
        basename = os.path.basename(filename)
        while any(basename.endswith("." + ext) for ext in EXTENSIONS):
            basename = basename[:basename.rfind('.')]
        phuInfo['basename'] = basename
        return phuInfo, infoList

    def translate_visit(self, md):
        visit = self._counter
        self._counter -= 1
        return visit

    def translate_ccd(self, md):
        return 0  # There's only one

    def translate_filter(self, md):
        return filters[md.get("FILTER")]


class MonocamRegisterTask(RegisterTask):
    def addVisits(self, conn, dryrun=False, table=None):
        # Set the visit numbers to match the 'id' field
        if table is None:
            table = self.config.table
        sql = "UPDATE %s SET visit = id" % table
        if dryrun:
            print "Would execute: %s" % sql
        else:
            conn.execute(sql)
        return RegisterTask.addVisits(self, conn, dryrun=dryrun, table=table)


class MonocamIngestTask(IngestTask):
    def ingest(self, infile, outfile, mode="move", dryrun=False):
        """Ingest a file into the image repository.

        @param infile  Name of input file
        @param outfile Name of output file (file in repository)
        @param mode    Mode of ingest (copy/link/move/skip)
        @param dryrun  Only report what would occur?
        @param Success boolean
        """
        if mode == "skip":
            return True
        if mode != "copy":
            raise RuntimeError("Mode '%s' not supported, only 'copy' and 'skip' "
                               "because we're munging the headers" % mode)
        try:
            outdir = os.path.dirname(outfile)
            if not os.path.isdir(outdir):
                try:
                    os.makedirs(outdir)
                except:
                    # Silently ignore mkdir failures due to race conditions
                    if not os.path.isdir(outdir):
                        raise
            if self.config.clobber and os.path.lexists(outfile):
                os.unlink(outfile)
            assertCanCopy(infile, outfile)

            if dryrun:
                self.log.info("Would munge headers of %s to %s" % (infile, outfile))
                return True

            # Read the file, add a Wcs and output it
            md = readMetadata(infile, 1)
            image = DecoratedImageU(infile)
            data = joinShutter(md.get("DATE-OBS"))
            wcs = makeWcs(IcrsCoord(data.ra*degrees, data.dec*degrees),
                          Point2D(0.5*image.getWidth(), 0.5*image.getHeight()),
                          PIXELSCALE/3600.0, 0.0, 0.0, PIXELSCALE/3600.0).getFitsMetadata()
            for key in wcs.names():
                md.set(key, wcs.get(key))
            image.writeFits(outfile)
            print "%s --<munge>--> %s" % (infile, outfile)
        except Exception, e:
            self.log.warn("Failed to %s %s to %s: %s" % (mode, infile, outfile, e))
            if not self.config.allowError:
                raise
            return False
        return True


    def run(self, args):
        """Open the database"""
        getDatabase(args.butler.repository._mapper.root)
        return IngestTask.run(self, args)

##############################################################################################################

class MonocamCalibsParseTask(CalibsParseTask):
    def _translateFromCalibId(self, field, md):
        data = md.get("CALIB_ID")
        match = re.search(".*%s=(\S+)" % field, data)
        return match.groups()[0]

    def translate_ccd(self, md):
        return self._translateFromCalibId("ccd", md)

    def translate_filter(self, md):
        return self._translateFromCalibId("filter", md)

    def translate_calibDate(self, md):
        return self._translateFromCalibId("calibDate", md)
