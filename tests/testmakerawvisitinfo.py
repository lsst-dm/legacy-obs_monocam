
# coding: utf-8

# In[ ]:

from __future__ import absolute_import, division, print_function

import math
import os
import warnings
import unittest
import lsst.utils.tests

from lsst.daf.base import DateTime
import lsst.afw.image as afwImage
import lsst.utils.tests
from lsst.utils import getPackageDir

import lsst.pex.exceptions as pexExcept
import lsst.daf.persistence as dafPersist
from lsst.obs.base import MakeRawVisitInfo
from lsst.afw.image import VisitInfo
RotType = VisitInfo.getRotType
from lsst.afw.coord import IcrsCoord, Coord
from lsst.afw.geom import degrees

import pyfits


# In[ ]:

datadir = "/Users/lsst/monocam_13_support/obs_monocam/tests/"
raw = datadir + "raw/lsst1532+1/SDSSG/2016-05-04lsst1532+13_scienceII_01.fits" # visit number 33
bias = datadir + "raw/BIAS/OPEN/2016-05-05morningbias_50.fits"
flat = datadir + "raw/FLAT/SDSSG/2016-05-05flat_G.fits"


# In[ ]:

fitslist = [raw, bias, flat]
fitsvisit = []
for fits in fitslist:
    hdulist = pyfits.open(fits)
    hdulist.close()
    prihdr = hdulist[0].header
    fitsvisit.append(prihdr['VISIT'])


# In[ ]:

hdulist = pyfits.open(raw)
hdulist.close()
prihdr = hdulist[0].header

boresightRaDec = IcrsCoord(prihdr["RA"], prihdr["DEC"])

lst = float("nan")
era = lst

raw_visit_info = {
    "dateAvg": DateTime(prihdr["DATE-OBS"], DateTime.TAI),
    "exposureTime": prihdr["EXPTIME"],
    "darkTime": prihdr["DARKTIME"],
    "era": era,
    "boresightRaDec": boresightRaDec,
    "boresightAzAlt": float("nan"),
    "boresightAirmass": prihdr["AIRMASS"],
    "boresightRotAngle": float("nan")*degrees,
    "rotType": float("nan"),
    "obs_longitude": -111.740278*degrees,
    "obs_latitude": 35.184167*degrees,
    "obs_elevation": 2273, # meters
    "weath_airTemperature": float("nan"),
    "weath_airPressure": float("nan"),
    "weath_humidity": float("nan")}


# In[ ]:

# most of this code is taken from : https://github.com/lsst/obs_decam/blob/master/tests/testGetRaw.py

class GetRawTestCase(lsst.utils.tests.TestCase):
    
    def setUp(self):
#         self.repoPath = os.path.join(datadir, "data")
        self.repoPath = datadir
        calibPath = os.path.join(datadir, "data/calib")
#         self.butler = dafPersist.Butler(root=self.repoPath, calibRoot=calibPath)
        self.butler = dafPersist.Butler(root=self.repoPath)
        
#         self.size = (2160, 4146)
        self.dataId = {'visit': fitsvisit[0]}
        self.filter = "g"
    
    def testPackageName(self):
        name = dafPersist.Butler.getMapperClass(root=self.repoPath).packageName
        self.assertEqual(name, "obs_monocam")

    def testRaw(self):
        """Test retrieval of raw image"""
        exp = self.butler.get("raw", visit=fitsvisit[0])

        print("dataId: %s" % self.dataId)
        print("width: %s" % exp.getWidth())
        print("height: %s" % exp.getHeight())
        print("detector id: %s" % exp.getDetector().getId())

#         self.assertEqual(exp.getWidth(), self.size[0])
#         self.assertEqual(exp.getHeight(), self.size[1])
#         self.assertEqual(exp.getDetector().getId(), self.dataId["ccdnum"])
        self.assertEqual(exp.getFilter().getFilterProperty().getName(), self.filter)
        self.assertTrue(exp.hasWcs())

        # Metadata which should have been copied from zeroth extension.
        visitInfo = exp.getInfo().getVisitInfo()
        self.assertEqual(visitInfo.getDate(), raw_visit_info['dateAvg'])
        self.assertEqual(visitInfo.getExposureTime(), raw_visit_info['exposureTime'])
        self.assertEqual(visitInfo.getDarkTime(), raw_visit_info['darkTime'])
        visitInfo = exp.getInfo().getVisitInfo()
        self.assertEqual(visitInfo.getDate(), raw_visit_info['dateAvg'])
        self.assertAnglesNearlyEqual(visitInfo.getEra(), raw_visit_info['era'])
        self.assertCoordsNearlyEqual(visitInfo.getBoresightRaDec(), raw_visit_info['boresightRaDec'])
        self.assertCoordsNearlyEqual(visitInfo.getBoresightAzAlt(), raw_visit_info['boresightAzAlt'])
        self.assertAlmostEqual(visitInfo.getBoresightAirmass(), raw_visit_info['boresightAirmass'])
        self.assertTrue(math.isnan(visitInfo.getBoresightRotAngle().asDegrees()))
        self.assertEqual(visitInfo.getRotType(), raw_visit_info['rotType'])
        observatory = visitInfo.getObservatory()
        self.assertAnglesNearlyEqual(observatory.getLongitude(), raw_visit_info['obs_longitude'])
        self.assertAnglesNearlyEqual(observatory.getLatitude(), raw_visit_info['obs_latitude'])
        self.assertAlmostEqual(observatory.getElevation(), raw_visit_info['obs_elevation'])
#         weather = visitInfo.getWeather()
#         self.assertAlmostEqual(weather.getAirTemperature(), raw_visit_info['weath_airTemperature'])
#         self.assertAlmostEqual(weather.getAirPressure(), raw_visit_info['weath_airPressure'])
#         self.assertAlmostEqual(weather.getHumidity(), raw_visit_info['weath_humidity'])

        # Example of metadata which should *not* have been copied from zeroth extension.
        self.assertNotIn("PROPOSER", exp.getMetadata().paramNames())
        
#     def testRawMetadata(self):
#         """Test retrieval of metadata"""
#         md = self.butler.get("calibs")
#         print("EXPNUM(visit): %s" % md.get('EXPNUM'))
#         print("ccdnum: %s" % md.get('CCDNUM'))
#         self.assertEqual(md.get('EXPNUM'), self.dataId["visit"])
#         self.assertEqual(md.get('CCDNUM'), self.dataId["ccdnum"])
        
    def testBias(self):
        """Test retrieval of bias image"""
        exp = self.butler.get("raw", visit=fitsvisit[1])
        print("dataId: %s" % self.dataId)
        print("detector id: %s" % exp.getDetector().getId())
#         self.assertEqual(exp.getDetector().getId(), self.dataId["ccdnum"])
#         self.assertTrue(exp.hasWcs())
        
    def testFlat(self):
        """Test retrieval of flat image"""
        exp = self.butler.get("raw", visit=fitsvisit[2])
        print("dataId: %s" % self.dataId)
        print("detector id: %s" % exp.getDetector().getId())
        print("filter: %s" % self.filter)
#         self.assertEqual(exp.getDetector().getId(), self.dataId["ccdnum"])
        self.assertEqual(exp.getFilter().getFilterProperty().getName(), self.filter)
#         self.assertTrue(exp.hasWcs())


# In[ ]:

if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()


# In[ ]:

# print(butler.get('raw', visit=33).getInfo().getVisitInfo())


# In[ ]:

# for x in butler.subset('raw', visit=10005): print(x.dataId)


# In[ ]:

# butler = dafPersist.Butler("/Users/lsst/monocam_13_support/obs_monocam/tests/")
# butler.get("raw", visit=33, filter="SDSSG", expTime=50.0)


# In[ ]:

# butler.get("bias", dataId={'visit': 33})


# In[ ]:

# repoPath = os.path.join(datadir, "data")
# calibPath = os.path.join(datadir, "data/calib")
# butler = dafPersist.Butler(root=repoPath, calibRoot=calibPath)

