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
import os
import sys
import unittest

import lsst.utils.tests
from lsst.utils import getPackageDir
from lsst.afw.geom import Extent2I
import lsst.obs.base.tests
from lsst.afw.coord import IcrsCoord

class TestObsTest(lsst.obs.base.tests.ObsTests, lsst.utils.tests.TestCase):
    def setUp(self):
        product_dir = getPackageDir('obs_monocam')
        data_dir = os.path.join(getPackageDir("obs_monocam"), "tests", "data")
        raw = data_dir + "/raw/lsst1532+1/SDSSG/2016-05-04lsst1532+13_scienceII_01.fits" # visit number 33
        bias = data_dir + "/bias/2016-05-05/bias-2016-05-05.fits.gz"
        flat = data_dir + "/flat/SDSSG/2016-05-05/flat_SDSSG_2016-05-05.fits.gz"

        fitslist = [raw, bias, flat]
        fitsvisit = [33, 100008, 10005]
        fitsdate = ['2016-05-04T07:37:53.225', '2016-05-05T12:44:09.441', '2016-05-05T03:17:08.930']
        fitsfilter = ['SDSSG', 'OPEN', 'SDSSG']
        exptime = [300.0004, float('nan'), float('nan')]
        ra = '15:32:09.78'
        dec = '+13:56:15.6'

        butler = lsst.daf.persistence.Butler(root=data_dir)
        mapper = lsst.obs.monocam.MonocamMapper(root=data_dir)
       
        dataIds = {'raw':  {'visit': fitsvisit[0], 'filter': fitsfilter[0], 'date': fitsdate[0][:10]},
                   'bias': {'visit': fitsvisit[1], 'filter': fitsfilter[1], 'date': fitsdate[1][:10]},
                   'flat': {'visit': fitsvisit[2], 'filter': fitsfilter[2], 'date': fitsdate[2][:10]},
                   'dark': unittest.SkipTest
                   }
        self.setUp_tests(butler, mapper, dataIds)

        ccdExposureId_bits = 41
        exposureIds = {'raw': fitsvisit[0], 'bias': fitsvisit[1], 'flat': fitsvisit[2]}
        filters = {'raw': fitsfilter[0], 'bias': fitsfilter[1], 'flat': fitsfilter[2]}
        exptimes = {'raw': exptime[0], 'bias': exptime[1], 'flat': exptime[2]}
        detectorIds = {'raw': 0, 'bias': 0, 'flat': 0}
        detector_names = {'raw': '0', 'bias': '0', 'flat': '0'}
        detector_serials = {'raw': 'abcd1234', 'bias': 'abcd1234', 'flat': 'abcd1234'}
        dimensions = {'raw': Extent2I(544, 2048),
                      'bias': Extent2I(4096, 4004),
                      'flat': Extent2I(4096, 4004)
                      }
        sky_origin = IcrsCoord(ra, dec)
        sky_origin = (sky_origin[0].asDegrees(), sky_origin[1].asDegrees())

        raw_subsets = (({'filter': fitsfilter[0]}, 1), ({'filter': fitsfilter[0]}, 1), ({'filter': fitsfilter[0]}, 1))
        linearizer_type = unittest.SkipTest
        self.setUp_butler_get(ccdExposureId_bits=ccdExposureId_bits,
                              exposureIds=exposureIds,
                              filters=filters,
                              exptimes=exptimes,
                              detectorIds=detectorIds,
                              detector_names=detector_names,
                              detector_serials=detector_serials,
                              dimensions=dimensions,
                              sky_origin=sky_origin,
                              raw_subsets=raw_subsets,
                              linearizer_type=linearizer_type
                              )

#        path_to_raw = os.path.join(data_dir, "raw", "lsst1532+1", "SDSSG", "2016-05-04lsst1532+13_scienceII_01.fits")
        path_to_raw = os.path.join(data_dir, "raw_fits", "2016-05-04lsst1532+13_scienceII_01.fits.gz")
#        keys = set(('filter', 'name', 'patch', 'tract', 'visit', 'pixel_id'))
        keys = set(('calibDate', 'basename', 'object', 'channel', 'filter', 'name', 'patch', 'tract', 'visit', 'pixel_id'))

        query_format = ["visit", "filter"]
#        queryMetadata = (({'visit': fitsvisit[0]}, [(1, 'g')]),
#                         ({'visit': fitsvisit[1]}, [(2, 'g')]),
#                         ({'visit': fitsvisit[2]}, [(3, 'r')]),
#                         ({'filter': 'g'}, [(1, 'g'), (2, 'g')]),
#                         ({'filter': 'r'}, [(3, 'r')]),
#                         )
        queryMetadata = (({'visit': fitsvisit[0], 'filter': fitsfilter[0]}, [(fitsvisit[0], fitsfilter[0])]),
                         ({'visit': fitsvisit[0], 'filter': fitsfilter[0]}, [(fitsvisit[0], fitsfilter[0])]),
                         ({'visit': fitsvisit[0], 'filter': fitsfilter[0]}, [(fitsvisit[0], fitsfilter[0])]))

                         
        map_python_type = 'lsst.afw.image.DecoratedImageU'
        map_cpp_type = 'DecoratedImageU'
        map_storage_name = 'FitsStorage'
        metadata_output_path = os.path.join(data_dir, 'processCcd_metadata', 'v' + str(fitsvisit[0]) + '_f' + fitsfilter[0] + '.boost')
        raw_filename = '2016-05-04lsst1532+13_scienceII_01.fits'
        default_level = 'visit'
        raw_levels = (
            ('raw', set({'basename': str, 
                'visit': int,
                'ccd': int,
                'filter': str,
                'date': str,
                'expTime': float,
                'object': str,
                'imageType': str,
                })), 
                 ('raw_amp', set({'basename': str, 'visit': int,
                'ccd': int,
                'filter': str,
                'date': str,
                'expTime': float,
                'object': str,
                'imageType': str,
                }))                      
        )
        
        self.setUp_mapper(output=data_dir,
                          path_to_raw=path_to_raw,
                          keys=keys,
                          query_format=query_format,
                          queryMetadata=queryMetadata,
                          metadata_output_path=metadata_output_path,
                          map_python_type=map_python_type,
                          map_cpp_type=map_cpp_type,
                          map_storage_name=map_storage_name,
                          raw_filename=raw_filename,
                          default_level=default_level,
                          raw_levels=raw_levels,
                          )

        self.setUp_camera(camera_name='monocam',
                          n_detectors=1,
                          first_detector_name='0',
                          )

        super(TestObsTest, self).setUp()


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == '__main__':
    setup_module(sys.modules[__name__])
    unittest.main()
