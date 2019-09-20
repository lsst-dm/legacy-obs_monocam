"""
Monocam-specific overrides for ProcessCcdTask
"""
import os.path

from lsst.utils import getPackageDir
from lsst.obs.monocam import MonocamIsrTask
from lsst.meas.algorithms import LoadIndexedReferenceObjectsTask

obsConfigDir = os.path.join(getPackageDir("obs_monocam"), "config")

config.isr.retarget(MonocamIsrTask)
config.isr.load(os.path.join(obsConfigDir, "isr.py"))

config.charImage.repair.doCosmicRay = True
config.charImage.repair.cosmicray.nCrPixelMax = 1000000

config.charImage.background.binSize = 128
config.charImage.detection.background.binSize = 128
config.calibrate.detection.background.binSize = 128
config.charImage.background.useApprox = False
config.charImage.detection.background.useApprox = False
config.calibrate.detection.background.useApprox = False

#config.charImage.refObjLoader.retarget(LoadIndexedReferenceObjectsTask)
#config.calibrate.astromRefObjLoader.retarget(LoadIndexedReferenceObjectsTask)
#config.calibrate.photoRefObjLoader.retarget(LoadIndexedReferenceObjectsTask)

#config.calibrate.astromRefObjLoader.filterMap = {'SDSSG':'G',  'SDSSR':'R', 'SDSSI':'I', 'SDSSZ':'Z'}
#config.calibrate.photoRefObjLoader.filterMap = {'SDSSG':'G', 'SDSSR':'R', 'SDSSI':'I', 'SDSSZ':'Z'}
#config.charImage.refObjLoader.filterMap = {'SDSSG':'G', 'SDSSR':'R', 'SDSSI':'I', 'SDSSZ':'Z'}

#config.calibrate.astrometry.matcher.numBrightStars=200
#config.calibrate.photoCal.matcher.numBrightStars=200

config.calibrate.astromRefObjLoader.filterMap = {'SDSSG':'g',  'SDSSR':'r', 'SDSSI':'i', 'SDSSZ':'z'}
config.calibrate.photoRefObjLoader.filterMap = {'SDSSG':'g', 'SDSSR':'r', 'SDSSI':'i', 'SDSSZ':'z'}
config.charImage.refObjLoader.filterMap = {'SDSSG':'g', 'SDSSR':'r', 'SDSSI':'i', 'SDSSZ':'z'}

# PSFEx gives better PSFs for HSC
try:
    import lsst.meas.extensions.psfex.psfexPsfDeterminer
    config.charImage.measurePsf.psfDeterminer["psfex"].spatialOrder = 2
    config.charImage.measurePsf.psfDeterminer.name = "psfex"
except ImportError as e:
    print("WARNING: Unable to use psfex: %s" % e)
    config.charImage.measurePsf.psfDeterminer.name = "pca"

if False:
    # we don't have astrometry_net data (yet) so astrom and photo cal are impossible
    config.doCalibrate = False
elif True:
    # Running on sky data from USNO
    # We need to blind-solve because we don't trust the Wcs
    from lsst.meas.extensions.astrometryNet import ANetAstrometryTask
    config.calibrate.astrometry.retarget(ANetAstrometryTask)
    for ff in "griz":
        config.calibrate.astrometry.solver.filterMap["SDSS" + ff.upper()] = ff
    config.calibrate.astrometry.solver.useWcsRaDecCenter = False  # It's off for some reason dunno yet
    config.calibrate.astrometry.solver.useWcsParity = False  # I doubt I guess right
    config.calibrate.astrometry.solver.useWcsPixelScale = False  # DGM says it's 0.4, but....
else:
    # Using default astrometry matcher
    for ff in "griz":
        config.calibrate.refObjLoader.filterMap["SDSS" + ff.upper()] = ff
