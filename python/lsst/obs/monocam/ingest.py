from __future__ import print_function
import os
import re
from lsst.pipe.tasks.ingest import IngestTask, ParseTask, RegisterTask
from lsst.pipe.tasks.ingestCalibs import CalibsParseTask
from .hack import getDatabase, getHeader, getDateFromHeader, getShutterData

# Lookup table for lab data
# XXX This is completely made up and needs to be updated with the real values when they become available.
filters = {
    0: 'u',
    1: 'g',
    2: 'r',
    3: 'i',
    4: 'z',
    5: 'y',
    "UNK": "UNKNOWN",
}

EXTENSIONS = ["fits", "gz", "fz"]  # Filename extensions to strip off


class HackParseTask(ParseTask):
    """Parser that uses a hack to get information from the shutter files

    Use this to ingest data from USNO, where the camera files don't have the necessary
    header keywords and we have to correlate with the shutter files.
    """
    _counter = -1  # Visit counter; negative so it doesn't overlap with the 'id' field, which autoincrements

    def getInfo(self, filename):
        md = getHeader(filename)
        data = getShutterData(getDateFromHeader(md))
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
    """Parser suitable for lab data"""
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
    """Put data in the registry

    We set the visit number (required for various operations with the LSST stack)
    to match the auto-incremented ID in the registery. This is used for both lab
    data and USNO data since there is no exposure ID in the FITS headers of either.
    """

    def addVisits(self, conn, dryrun=False, table=None):
        """Set the visit numbers to match the 'id' field"""
        if table is None:
            table = self.config.table
        sql = "UPDATE %s SET visit = id" % table
        if dryrun:
            print("Would execute: %s" % sql)
        else:
            conn.execute(sql)
        return RegisterTask.addVisits(self, conn, dryrun=dryrun, table=table)


class MonocamIngestTask(IngestTask):
    """Ingest USNO monocam data

    This opens the database handle, used for the hack to support ingesting
    USNO monocam data.
    """

    def run(self, args):
        """Open the database"""
        getDatabase(args.butler.repository._mapper.root)
        return IngestTask.run(self, args)


##############################################################################################################

class MonocamCalibsParseTask(CalibsParseTask):
    """Parser for calibs"""

    def _translateFromCalibId(self, field, md):
        """Get a value from the CALIB_ID written by constructCalibs"""
        data = md.get("CALIB_ID")
        match = re.search(".*%s=(\S+)" % field, data)
        return match.groups()[0]

    def translate_ccd(self, md):
        return self._translateFromCalibId("ccd", md)

    def translate_filter(self, md):
        return self._translateFromCalibId("filter", md)

    def translate_calibDate(self, md):
        return self._translateFromCalibId("calibDate", md)
