
# coding: utf-8

from __future__ import absolute_import, division, print_function

import math
import os
import warnings
import unittest
import lsst.utils.tests

import lsst.daf.persistence as dafPersist

from lsst.daf.base import DateTime
from lsst.utils import getPackageDir
from lsst.afw.image import RotType_UNKNOWN
from lsst.afw.coord import IcrsCoord, Coord
from lsst.afw.geom import degrees, Angle

import pyfits

datadir = os.path.join(getPackageDir("obs_monocam"), "tests", "data")
raw = datadir + "/raw/lsst1532+1/SDSSG/2016-05-04lsst1532+13_scienceII_01.fits" # visit number 33
bias = datadir + "/bias/2016-05-05/bias-2016-05-05.fits.gz"
flat = datadir + "/flat/SDSSG/2016-05-05/flat_SDSSG_2016-05-05.fits.gz"

fitslist = [raw, bias, flat]
fitsvisit, fitsdate, fitsfilter, exptime = [], [], [], []

for fits in fitslist:
    if fits == raw:
        hdulist = pyfits.open(fits)
        hdulist.close()
        prihdr = hdulist[0].header
        fitsvisit.append(prihdr['VISIT'])
        fitsdate.append(prihdr["DATE-OBS"])
        fitsfilter.append(prihdr["FILTER"])

hdulist = pyfits.open(raw)
hdulist.close()
prihdr = hdulist[0].header

nanFloat = float("nan")
nanAngle = Angle(nanFloat)
era = nanAngle

boresightRaDec = IcrsCoord(prihdr["RA"], prihdr["DEC"])

prihdr = hdulist[0].header
raw_visit_info = {
    "dateAvg": DateTime(prihdr["DATE-OBS"], DateTime.TAI),
    "exposureTime": prihdr["EXPTIME"],
    "darkTime": prihdr["DARKTIME"],
    "era": era,
    "boresightRaDec": boresightRaDec,
    "boresightAzAlt": Coord(nanAngle, nanAngle),
    "boresightAirmass": prihdr["AIRMASS"],
    "boresightRotAngle": nanFloat*degrees,
    "rotType": RotType_UNKNOWN,
    "obs_longitude": -111.740278*degrees,
    "obs_latitude": 35.184167*degrees,
    "obs_elevation": 2273, # meters
    "weath_airTemperature": nanFloat,
    "weath_airPressure": nanFloat,
    "weath_humidity": nanFloat}


# most of this code is taken from : https://github.com/lsst/obs_decam/blob/master/tests/testGetRaw.py

class GetRawTestCase(lsst.utils.tests.TestCase):
    
    def setUp(self):
        self.repoPath = datadir
        self.butler = dafPersist.Butler(root=self.repoPath)
        
        self.size = (544, 2048)
        self.dataId = {'visit': fitsvisit[0], 'ccdnum': 0}
        self.filter = "g"
    
    def testPackageName(self):
        name = dafPersist.Butler.getMapperClass(root=self.repoPath).packageName
        self.assertEqual(name, "obs_monocam")

    def testRaw(self):
        """Test retrieval of raw image"""
        exp = self.butler.get("raw", visit = fitsvisit[0])

        print("dataId: %s" % self.dataId)
        print("width: %s" % exp.getWidth())
        print("height: %s" % exp.getHeight())
        print("detector id: %s" % exp.getDetector().getId())
        
        self.assertEqual(exp.getWidth(), self.size[0])
        self.assertEqual(exp.getHeight(), self.size[1])
        self.assertEqual(exp.getDetector().getId(), self.dataId["ccdnum"])
        self.assertEqual(exp.getFilter().getFilterProperty().getName(), self.filter)
        self.assertTrue(exp.hasWcs())

        # Metadata which should have been copied from zeroth extension.
        visitInfo = exp.getInfo().getVisitInfo()
#        self.assertEqual(visitInfo.getDate(), raw_visit_info['dateAvg'])
        self.assertEqual(visitInfo.getExposureTime(), raw_visit_info['exposureTime'])
        self.assertEqual(visitInfo.getDarkTime(), raw_visit_info['darkTime'])
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
        
#     def testRawMetadata(self):
#         """Test retrieval of metadata"""
#         md = self.butler.get("calibs")
#         print("EXPNUM(visit): %s" % md.get('EXPNUM'))
#         print("ccdnum: %s" % md.get('CCDNUM'))
#         self.assertEqual(md.get('EXPNUM'), self.dataId["visit"])
#         self.assertEqual(md.get('CCDNUM'), self.dataId["ccdnum"])
        
    def testBias(self):
        """Test retrieval of bias image"""
#        exp = self.butler.get("bias", visit = fitsvisit[1], filter=fitsfilter[1], date = fitsdate[1][:10])
        exp = self.butler.get("bias", filter="NONE", date="2016-05-05")
        print("detector id: %s" % exp.getDetector().getId())
        self.assertEqual(exp.getDetector().getId(), self.dataId["ccdnum"])
        
    def testFlat(self):
        """Test retrieval of flat image"""
#        exp = self.butler.get("flat", visit = fitsvisit[2], filter=fitsfilter[2], date = fitsdate[2][:10])
        exp = self.butler.get("flat", filter="SDSSG")
        print("detector id: %s" % exp.getDetector().getId())
        print("filter: %s" % self.filter)
        self.assertEqual(exp.getDetector().getId(), self.dataId["ccdnum"])
        self.assertEqual(exp.getFilter().getFilterProperty().getName(), self.filter)

if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()