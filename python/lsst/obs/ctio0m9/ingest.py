from __future__ import print_function
import os
import re
from lsst.pipe.tasks.ingest import ParseTask
from lsst.pipe.tasks.ingestCalibs import CalibsParseTask


EXTENSIONS = ["fits", "gz", "fz"]  # Filename extensions to strip off


class Ctio0m9ParseTask(ParseTask):
    """Parser suitable for lab data"""

    def getInfo(self, filename):
        # Grab the basename
        phuInfo, infoList = ParseTask.getInfo(self, filename)
        basename = os.path.basename(filename)
        while any(basename.endswith("." + ext) for ext in EXTENSIONS):
            basename = basename[:basename.rfind('.')]
        phuInfo['basename'] = basename
        return phuInfo, infoList
 
    def translate_ccd(self, md):
        return 0  # There's only one

    def translate_visit(self, md):
        kwd = md.get("ID")
        out = re.sub("[^0-9]", "", kwd)
        print ('VISIT :%s'%out)

        kwd = md.get("TSEC22") 
        print ('AMP22 :%s'%kwd)
        return int(out)

    def translate_amp(self, md):
        kwd = md.get("TSEC12")
        
        print ('AMP :%s'%kwd)
        return kwd

    
    
    def translate_filter(self, md):
        kwd = md.get("FILTERS")
        out = re.sub(r"\W", "_", kwd)
        print ('FILTERS :%s'%out)
        return out

   
##############################################################################################################

class Ctio0m9CalibsParseTask(CalibsParseTask):
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
