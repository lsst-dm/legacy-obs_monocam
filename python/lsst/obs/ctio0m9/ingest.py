from __future__ import print_function
import os
import re
from lsst.pipe.tasks.ingest import ParseTask
from lsst.pipe.tasks.ingestCalibs import CalibsParseTask
import lsst.afw.image as afwImage

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
        out = re.sub("[^0-9]", "", kwd)[4:-1]
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

   
##########################################################################

class Ctio0m9CalibsParseTask(CalibsParseTask):
    """Parser for calibs"""

    def _translateFromCalibId(self, field, md):
        """Get a value from the CALIB_ID written by constructCalibs"""
        data = md.get("DATE")
        print('date :%s '%(data))
        match = re.search(".*%s=(\S+)" % field, data)
        print('match :%s '%(match))
        return match.groups()[0]



    def translate_filter(self, md):
        kwd = md.get("FILTERS")
        out = re.sub(r"\W", "_", kwd)
        print ('FILTERS :%s'%out)
        return out

    
    def translate_calibDate(self, md):
        date = md.get("DATE")
        date = date.split('T')[0]
        print('date : %s '%(date))
        return date


    def getInfo(self, filename):
        # Grab the basename
        phuInfo, infoList = ParseTask.getInfo(self, filename)
        basename = os.path.basename(filename)
        while any(basename.endswith("." + ext) for ext in EXTENSIONS):
            basename = basename[:basename.rfind('.')]
        phuInfo['basename'] = basename
        return phuInfo, infoList
 
    def translate_ccd(self, md):
        return 1  # There's only one

    def translate_visit(self, md):
        kwd = md.get("ID")
        out = re.sub("[^0-9]", "", kwd)[4:-1]
        print ('VISIT :%s'%out)

        kwd = md.get("TSEC22") 
        print ('AMP22 :%s'%kwd)
        return int(out)

    def translate_amp(self, md):
        kwd = md.get("TSEC12")
        
        print ('AMP :%s'%kwd)
        return kwd


    
    
    # Added following advice from S. Krughoff
    #https://lsstc.slack.com/messages/dm-obs-packges/
    def getCalibType(self, filename):
        """Return a a known calibration dataset type using
        the observation type in the header keyword OBSTYPE

        @param filename: Input filename
        """
        md = afwImage.readMetadata(filename, self.config.hdu)
        if not md.exists("OBJECT"):
            raise RuntimeError("Unable to find the required header keyword OBJECT")
        obstype = md.get("OBJECT").strip().lower()
        if "flat" in obstype:
            obstype = "flat"
        elif "zero" in obstype or "bias" in obstype:
            obstype = "bias"
        elif "dark" in obstype:
            obstype = "dark"
        elif "fringe" in obstype:
            obstype = "fringe"
        return obstype

