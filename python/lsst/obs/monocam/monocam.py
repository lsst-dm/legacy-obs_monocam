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
import warnings

import numpy
import lsst.afw.cameraGeom as cameraGeom
import lsst.geom as geom
import lsst.afw.geom as afwGeom
from lsst.obs.base import MakeRawVisitInfo
from lsst.afw.coord import Observatory
from lsst.geom import SpherePoint, degrees


__all__ = ["Monocam"]


class Monocam(cameraGeom.Camera):
    """The monocam Camera

    There is one ccd with name "0"
    It has sixteen amplifiers with names like "00".."07" and "10".."17"

    Standard keys are:
    amp: amplifier name: one of 00, 01, 02, 03, 04, 05, 06, 07, 10, 11, 12,
                                13, 14, 15, 16, 17
    ccd: ccd name: always 0
    visit: exposure number; this will be provided by the DAQ
    """
    # Taken from fit4_20160413-154303.pdf
    gain = {(0, 0): 3.707220,
            (1, 0): 3.724264,
            (2, 0): 3.758828,
            (3, 0): 3.794040,
            (4, 0): 3.724264,
            (5, 0): 3.776352,
            (6, 0): 3.758828,
            (7, 0): 3.776352,
            (0, 1): 3.724264,
            (1, 1): 3.657009,
            (2, 1): 3.640573,
            (3, 1): 3.624284,
            (4, 1): 3.640573,
            (5, 1): 3.707220,
            (6, 1): 3.673594,
            (7, 1): 3.640573}

    readNoise = {(0, 0): 7.105902,
                 (1, 0): 6.860052,
                 (2, 0): 7.387405,
                 (3, 0): 7.222204,
                 (4, 0): 7.250763,
                 (5, 0): 7.315250,
                 (6, 0): 7.104838,
                 (7, 0): 7.272336,
                 (0, 1): 8.485139,
                 (1, 1): 8.022778,
                 (2, 1): 8.157399,
                 (3, 1): 8.021112,
                 (4, 1): 8.015486,
                 (5, 1): 7.928829,
                 (6, 1): 16.031720,
                 (7, 1): 7.938155}

    def __new__(cls):
        """Construct a TestCamera
        """
        plateScale = afwGeom.Angle(13.55, afwGeom.arcseconds)  # plate scale, in angle on sky/mm
        radialDistortion = 0.  # radial distortion in mm/rad^2
        radialCoeff = numpy.array((0.0, 1.0, 0.0, radialDistortion)) / plateScale.asRadians()
        fieldAngleToFocalPlane = afwGeom.makeRadialTransform(radialCoeff)
        focalPlaneToFieldAngle = fieldAngleToFocalPlane.inverted()

        camera = cameraGeom.Camera.Builder("monocam")
        cls._makeDetectors(camera, focalPlaneToFieldAngle)
        camera.setTransformFromFocalPlaneTo(cameraGeom.FIELD_ANGLE, focalPlaneToFieldAngle)
        return camera.finish()

    def __init__(self):
        pass

    @classmethod
    def _makeDetectors(cls, camera, focalPlaneToFieldAngle):
        """!Make a list of detectors

        Parameters
        ----------
        camera : `lsst.afw.cameraGeom.camera.Builder`
            Camera to append detectors to.
        focalPlaneToFieldAngle : `lsst.afw.geom.TransformPoint2ToPoint2`
            Transform from ``FOCAL_PLANE`` to ``FIELD_ANGLE`` coordinates
            in the forward direction.
        """
        warnings.warn("plateScale no longer an argument to cameraGeom.makeDetector. Tread carefully.")
        detectorConfigList = cls._makeDetectorConfigList()
        for detectorConfig in detectorConfigList:
            amplifiers = cls._makeAmplifierCatalog()
            detBuilder = cameraGeom.addDetectorBuilderFromConfig(
                camera,
                detectorConfig,
                amplifiers,
                focalPlaneToFieldAngle,
            )
            if detBuilder is None:
                raise RuntimeError("Could not add detector!")

    @classmethod
    def _makeDetectorConfigList(cls):
        """!Make a list of detector configs

        Returns
        -------
        detectorConfigList : `list` of `lsst.afw.cameraGeom.DetectorConfig`
           List of detector configs.
        """
        # There is only a single detector assumed perfectly centered and
        # aligned.
        detector0Config = cameraGeom.DetectorConfig()
        detector0Config.name = '0'
        detector0Config.id = 0
        detector0Config.serial = 'abcd1234'
        detector0Config.detectorType = 0
        # This is the orientation we need to put the serial direciton along
        # the x-axis
        detector0Config.bbox_x0 = 0
        detector0Config.bbox_x1 = 4095
        detector0Config.bbox_y0 = 0
        detector0Config.bbox_y1 = 4003
        detector0Config.pixelSize_x = 0.01  # in mm
        detector0Config.pixelSize_y = 0.01  # in mm
        detector0Config.transformDict.nativeSys = 'Pixels'
        detector0Config.transformDict.transforms = None
        detector0Config.refpos_x = 2001.5
        detector0Config.refpos_y = 2047.5
        detector0Config.offset_x = 0.0
        detector0Config.offset_y = 0.0
        detector0Config.transposeDetector = False
        detector0Config.pitchDeg = 0.0
        detector0Config.yawDeg = 0.0  # this is where chip rotation goes in.
        detector0Config.rollDeg = 0.0
        return [detector0Config]

    @classmethod
    def _makeAmplifierCatalog(cls):
        """Construct an amplifier catalog
        """
        # Much of this will need to be filled in when we know it.
        xDataExtent = 512  # trimmed
        yDataExtent = 2002

        extended = 10  # extended register
        h_overscan = 22  # number of overscan in x
        v_overscan = 46  # number of overscan in y

        xRawExtent = extended + h_overscan + xDataExtent
        yRawExtent = v_overscan + yDataExtent  # no prescan in vertical

        saturation = 65535
        # Linearity correction is still under discussion, so this is a
        # placeholder.
        linearityType = "PROPORTIONAL"
        linearityThreshold = 0
        linearityMax = saturation
        linearityCoeffs = [linearityThreshold, linearityMax]

        ampCatalog = []
        for ampY in (0, 1):
            for ampX in range(8):
                amplifier = cameraGeom.Amplifier.Builder()
                amplifier.setName("%d%d" % (ampX, ampY))

                if bool(ampY):
                    amplifier.setBBox(geom.Box2I(
                        geom.Point2I(ampX*xDataExtent, ampY*yDataExtent),
                        geom.Extent2I(xDataExtent, yDataExtent),
                    ))
                else:
                    amplifier.setBBox(geom.Box2I(
                        geom.Point2I((7 - ampX)*xDataExtent, ampY*yDataExtent),
                        geom.Extent2I(xDataExtent, yDataExtent),
                    ))

                # in raw frames; always LL because raws are in amp coords
                readCorner = cameraGeom.ReadoutCorner.LL
                # bias region
                x0Bias = extended + xDataExtent
                y0Data = 0
                x0Data = extended

                amplifier.setRawBBox(geom.Box2I(
                    geom.Point2I(0, 0),
                    geom.Extent2I(xRawExtent, yRawExtent),
                ))
                amplifier.setRawDataBBox(geom.Box2I(
                    geom.Point2I(x0Data, y0Data),
                    geom.Extent2I(xDataExtent, yDataExtent),
                ))
                amplifier.setRawHorizontalOverscanBBox(geom.Box2I(
                    geom.Point2I(x0Bias, y0Data),
                    geom.Extent2I(h_overscan, yDataExtent),
                ))
                amplifier.setRawVerticalOverscanBBox(geom.Box2I(
                    geom.Point2I(x0Data, y0Data+yDataExtent),
                    geom.Extent2I(xDataExtent, v_overscan),
                ))
                amplifier.setRawXYOffset(geom.Extent2I(ampX*xRawExtent, ampY*yRawExtent))
                amplifier.setReadoutCorner(readCorner)
                amplifier.setGain(cls.gain[(ampX, ampY)])
                amplifier.setReadNoise(cls.readNoise[(ampX, ampY)])
                amplifier.setSaturation(saturation)
                amplifier.setRawFlipX(bool(ampY))
                # flip data when assembling if in top of chip
                amplifier.setRawFlipY(bool(ampY))
                amplifier.setRawPrescanBBox(geom.Box2I())
                # linearity placeholder stuff
                amplifier.setLinearityCoeffs([float(val) for val in linearityCoeffs])
                amplifier.setLinearityType(linearityType)
                amplifier.setLinearityThreshold(linearityThreshold)
                amplifier.setLinearityMaximum(linearityMax)
                amplifier.setLinearityUnits("DN")

                ampCatalog.append(amplifier)
        return ampCatalog


class MakeMonocamRawVisitInfo(MakeRawVisitInfo):
    """Make a VisitInfo from the FITS header of a raw Monocam image"""
    observatory = Observatory(-111.740278*degrees, 35.184167*degrees, 2273)  # long, lat, elev

    def setArgDict(self, md, argDict):
        """Set an argument dict for VisitInfo and pop associated metadata
        @param[in,out] md  metadata, as an lsst.daf.base.PropertyList or
                           PropertySet
        @param[in,out] argdict  a dict of arguments
        """
        argDict["exposureTime"] = self.popFloat(md, "EXPTIME")
        argDict["date"] = self.getDateAvg(md=md, exposureTime=argDict["exposureTime"])
        try:
            isRaw = md.get('OBJECT') not in ['DARK', 'FLAT', 'BIAS']
        except Exception:
            isRaw = False
        if isRaw:
            argDict["darkTime"] = self.popFloat(md, "DARKTIME")
            argDict["boresightRaDec"] = SpherePoint(
                self.popAngle(md, "RA", units="h"),
                self.popAngle(md, "DEC")
            )
            argDict["boresightAirmass"] = self.popFloat(md, "AIRMASS")
            argDict["observatory"] = self.observatory

    def getDateAvg(self, md, exposureTime):
        """Return date at the middle of the exposure
        @param[in,out] md  FITS metadata; changed in place
        @param[in] exposureTime  exposure time in sec
        """
        startDate = self.popIsoDate(md, "DATE-OBS", timesys=None)
        return self.offsetDate(startDate, 0.5*exposureTime)
