from lsst.obs.monocam import MonocamIsrTask
config.isr.retarget(MonocamIsrTask)
# Configs to get going.
config.isr.doDark = False
config.isr.doBias = False
config.isr.doFlat = True
config.isr.doFringe = False

config.charImage.background.binSize = 128
config.charImage.detectAndMeasure.detection.background.binSize = 128
config.calibrate.detectAndMeasure.detection.background.binSize = 128
config.charImage.background.useApprox = False
config.charImage.detectAndMeasure.detection.background.useApprox = False
config.calibrate.detectAndMeasure.detection.background.useApprox = False

# These detectors are noisier than we claim they are in the variance map, so back off on the threshold
# At the same time, we need all the stars we can get since it's a small telescope with short exposures...
config.charImage.detectAndMeasure.detection.thresholdValue = 20
config.charImage.detectAndMeasure.detection.includeThresholdMultiplier = 1.0
config.calibrate.detectAndMeasure.detection.thresholdValue = 20
config.calibrate.detectAndMeasure.detection.includeThresholdMultiplier = 1.0

if False:
    # we don't have astrometry_net data (yet) so astrom and photo cal are impossible
    config.doCalibrate=False
else:
    # Running on sky data from USNO
    from lsst.meas.astrom import ANetAstrometryTask  # We need to blind-solve because we don't trust the Wcs
    config.calibrate.astrometry.retarget(ANetAstrometryTask)
    for ff in "griz":
        config.calibrate.astrometry.solver.filterMap["SDSS" + ff.upper()] = ff
    config.calibrate.astrometry.solver.useWcsRaDecCenter = False  # It's off for some reason dunno yet
    config.calibrate.astrometry.solver.useWcsParity = False  # I doubt I guess right
    config.calibrate.astrometry.solver.useWcsPixelScale = False  # DGM says it's 0.4, but....
