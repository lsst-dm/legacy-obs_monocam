from builtins import range
#
# LSST Data Management System
# Copyright 2016 LSST Corporation.
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
import numpy
import lsst.afw.cameraGeom as cameraGeom
import lsst.afw.geom as afwGeom
from lsst.afw.table import AmpInfoCatalog, AmpInfoTable, LL
from lsst.afw.cameraGeom.cameraFactory import makeDetector






class Ctio0m9(cameraGeom.Camera):
    """The ctio0m9 Camera

    Standard keys are:
    amp: amplifier name: one of 11, 12, 21, 22
    ccd: ccd name: always 0
    visit: exposure number; this will be provided by the DAQ
    """
    # Taken from fit4_20160413-154303.pdf
    gain = {(1, 1): 3.,
            (1, 2): 3.,
            (2, 1): 3.,
            (2, 2): 3.,}


    readNoise = {(1, 1): 8.,
                 (1, 2): 8.,
                 (2, 1): 8.,
                 (2, 2): 8.,}

    def __init__(self):
        """Construct a TestCamera
        """
        plateScale = afwGeom.Angle(13.55, afwGeom.arcseconds)  # plate scale, in angle on sky/mm
        radialDistortion   = 0.  # radial distortion in mm/rad^2
        radialCoeff        = numpy.array((0.0, 1.0, 0.0, radialDistortion))\
                             / plateScale.asRadians()
        focalPlaneToPupil  = afwGeom.RadialXYTransform(radialCoeff)
        pupilToFocalPlane  = afwGeom.InvertedXYTransform(focalPlaneToPupil)
        cameraTransformMap = cameraGeom.CameraTransformMap(cameraGeom.FOCAL_PLANE,
                                                           {cameraGeom.PUPIL: pupilToFocalPlane})
        detectorList = self._makeDetectorList(pupilToFocalPlane, plateScale)
        cameraGeom.Camera.__init__(self, "ctio0m9", detectorList, cameraTransformMap)

        
    def _makeDetectorList(self, focalPlaneToPupil, plateScale):
        """!Make a list of detectors

        @param[in] focalPlaneToPupil  lsst.afw.geom.XYTransform from FOCAL_PLANE to PUPIL coordinates
        @param[in] plateScale  plate scale, in angle on sky/mm
        @return a list of detectors (lsst.afw.cameraGeom.Detector)
        """
        detectorList = []
        detectorConfigList = self._makeDetectorConfigList()
        for detectorConfig in detectorConfigList:
            ampInfoCatalog = self._makeAmpInfoCatalog()
            detector = makeDetector(detectorConfig, ampInfoCatalog, focalPlaneToPupil)
            detectorList.append(detector)
        return detectorList

    
    def _makeDetectorConfigList(self):
        """!Make a list of detector configs

        @return a list of detector configs (lsst.afw.cameraGeom.DetectorConfig)
        """
        # There is only a single detector assumed perfectly centered and aligned.
        detector0Config = cameraGeom.DetectorConfig()
        detector0Config.name = '0'
        detector0Config.id = 0
        detector0Config.serial = 'abcd1234'
        detector0Config.detectorType = 0
        # This is the orientation we need to put the serial direciton along the x-axis
        detector0Config.bbox_x0 = 0
        detector0Config.bbox_x1 = 2048
        detector0Config.bbox_y0 = 0
        detector0Config.bbox_y1 = 2048
        detector0Config.pixelSize_x = 0.01  # in mm
        detector0Config.pixelSize_y = 0.01  # in mm
        detector0Config.transformDict.nativeSys = 'Pixels'
        detector0Config.transformDict.transforms = None
        detector0Config.refpos_x = 1024
        detector0Config.refpos_y = 1024
        detector0Config.offset_x = 0.0
        detector0Config.offset_y = 0.0
        detector0Config.transposeDetector = False
        detector0Config.pitchDeg = 0.0
        detector0Config.yawDeg = 0.0  # this is where chip rotation goes in.
        detector0Config.rollDeg = 0.0
        return [detector0Config]

    def _makeAmpInfoCatalog(self):
        """Construct an amplifier info catalog
        """
      
        extended   = 1024  # extended register
        x_overscan = 40  # number of overscan pixel in x
        saturation = 65535
        # Linearity correction is still under discussion, so this is a placeholder.
        linearityType      = "PROPORTIONAL"
        linearityThreshold = 0
        linearityMax       = saturation
        linearityCoeffs    = [linearityThreshold, linearityMax]
        schema             = AmpInfoTable.makeMinimalSchema()
        linThreshKey       = schema.addField('linearityThreshold', type=float)
        linMaxKey          = schema.addField('linearityMaximum', type=float)
        linUnitsKey        = schema.addField('linearityUnits', type=str, size=9)
        # end placeholder
        self.ampInfoDict = {}
        ampCatalog       = AmpInfoCatalog(schema)
      
        for ampY in range(1, 3):
            for ampX in range(1, 3):
                record = ampCatalog.addNew()
                record.setName("%d%d" % (ampX, ampY))
                print('Amp Name : %s, %s'%(ampX, ampY))

                if((ampX == 1) & (ampY == 1)):
                    record.setBBox(afwGeom.Box2I(afwGeom.Point2I(10, 0),
                                                 afwGeom.Extent2I(extended, extended),))
                    record.setRawVerticalOverscanBBox(afwGeom.Box2I(
                        afwGeom.Point2I(1044, 0),
                        afwGeom.Extent2I(x_overscan, extended),))   
                    record.setRawXYOffset(\
                        afwGeom.Extent2I(1084, 1024))

                    
                if((ampX == 1) & (ampY == 2)):
                    record.setBBox(afwGeom.Box2I(afwGeom.Point2I(1134, 0),
                                                 afwGeom.Extent2I(extended, extended),))
                    record.setRawVerticalOverscanBBox(afwGeom.Box2I(
                        afwGeom.Point2I(1084, 0),
                        afwGeom.Extent2I(x_overscan, extended),))   
                    record.setRawXYOffset(\
                        afwGeom.Extent2I(1084, 1024))

                    
                if((ampX == 2) & (ampY == 1)):
                    record.setBBox(afwGeom.Box2I(afwGeom.Point2I(10, 1024),
                                                 afwGeom.Extent2I(extended, extended),))
                    record.setRawVerticalOverscanBBox(afwGeom.Box2I(
                        afwGeom.Point2I(1044, 1024),
                        afwGeom.Extent2I(x_overscan, extended),))   
                    record.setRawXYOffset(\
                        afwGeom.Extent2I(1084, 1024))

                    
                if((ampX == 2) & (ampY == 2)):
                    record.setBBox(afwGeom.Box2I(afwGeom.Point2I(1134, 1024),
                                                 afwGeom.Extent2I(extended, extended),))
                    record.setRawVerticalOverscanBBox(afwGeom.Box2I(
                        afwGeom.Point2I(1084, 1024),
                        afwGeom.Extent2I(x_overscan, extended),))   
                    record.setRawXYOffset(\
                        afwGeom.Extent2I(1084, 1024))

                    
                readCorner = LL  # in raw frames; always LL because raws are in amp coords
                # bias region
                record.setRawBBox(afwGeom.Box2I(
                    afwGeom.Point2I(0, 0),
                    afwGeom.Extent2I(extended, extended),
                ))
                record.setRawDataBBox(afwGeom.Box2I(
                    afwGeom.Point2I(0,0),
                    afwGeom.Extent2I(extended, extended),
                ))
                
                
                record.setReadoutCorner(readCorner)
                record.setGain(self.gain[(ampX, ampY)])
                record.setReadNoise(self.readNoise[(ampX, ampY)])
                record.setSaturation(saturation)
                record.setHasRawInfo(True)
                record.setRawPrescanBBox(afwGeom.Box2I())
                # linearity placeholder stuff
                record.setLinearityCoeffs([float(val) for val in linearityCoeffs])
                record.setLinearityType(linearityType)
                record.set(linThreshKey, float(linearityThreshold))
                record.set(linMaxKey, float(linearityMax))
                record.set(linUnitsKey, "DN")
        return ampCatalog
