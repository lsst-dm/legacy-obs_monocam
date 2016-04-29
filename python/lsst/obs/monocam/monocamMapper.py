# 
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
# 
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the LSST License Statement and 
# the GNU General Public License along with this program.  If not, 
# see <http://www.lsstcorp.org/LegalNotices/>.
#

import os

import lsst.utils
import lsst.afw.image.utils as afwImageUtils
from lsst.daf.butlerUtils import CameraMapper
import lsst.pex.policy as pexPolicy
from .monocam import Monocam

__all__ = ["MonocamMapper"]

class MonocamMapper(CameraMapper):
    packageName = 'obs_monocam'

    def __init__(self, inputPolicy=None, **kwargs):
        policyFile = pexPolicy.DefaultPolicyFile(self.packageName, "monocamMapper.paf", "policy")
        policy = pexPolicy.Policy(policyFile)

        # Not sure about this, cargo culted
        self.doFootprints = False
        if inputPolicy is not None:
            for kw in inputPolicy.paramNames(True):
                if kw == "doFootprints":
                    self.doFootprints = True
                else:
                    kwargs[kw] = inputPolicy.get(kw)

        CameraMapper.__init__(self, policy, policyFile.getRepositoryPath(), **kwargs)

        # Ensure each dataset type of interest knows about the full range of keys available from the registry
        keys = {'visit': int,
                'ccd': int,
                'filter': str,
                'date': str,
                'dateObs': str,
                'expTime': float,
                'object': str
        }
        for name in ("raw",
                     # processCcd outputs
                     "postISRCCD", "calexp", "postISRCCD", "src", "icSrc", "srcMatch",
                     ):
            self.mappings[name].keyDict.update(keys)

        # @merlin, you should swap these out for the filters you actually intend to use.
        self.filterIdMap = {
                'u': 0, 'g': 1, 'r': 2, 'i': 3, 'z': 4, 'y': 5, 'i2': 5}

        # The LSST Filters from L. Jones 04/07/10
        afwImageUtils.defineFilter('u', 364.59)
        afwImageUtils.defineFilter('g', 476.31)
        afwImageUtils.defineFilter('r', 619.42)
        afwImageUtils.defineFilter('i', 752.06)
        afwImageUtils.defineFilter('z', 866.85)
        afwImageUtils.defineFilter('y', 971.68, alias=['y4']) # official y filter
        afwImageUtils.defineFilter('NONE', 0.0, alias=['no_filter'])

    def _extractDetectorName(self, dataId):
        return "0"

    def _computeCcdExposureId(self, dataId):
        """Compute the 64-bit (long) identifier for a CCD exposure.

        @param dataId (dict) Data identifier with visit
        """
        visit = dataId['visit']
        return long(visit)

    def bypass_ccdExposureId(self, datasetType, pythonType, location, dataId):
        return self._computeCcdExposureId(dataId)

    def bypass_ccdExposureId_bits(self, datasetType, pythonType, location, dataId):
        return 41

    def validate(self, dataId):
        visit = dataId.get("visit")
        if visit is not None and not isinstance(visit, int):
            dataId["visit"] = int(visit)
        return dataId

    def _setCcdExposureId(self, propertyList, dataId):
        propertyList.set("Computed_ccdExposureId", self._computeCcdExposureId(dataId))
        return propertyList

    def _makeCamera(self, policy, repositoryDir):
        """Make a camera (instance of lsst.afw.cameraGeom.Camera) describing the camera geometry
        """
        return Monocam()

    def bypass_defects(self, datasetType, pythonType, location, dataId):
        """ since we have no defects, return an empty list.  Fix this when defects exist """
        return []

    def _defectLookup(self, dataId):
        # Evidently this gets called first
        return "hack"
