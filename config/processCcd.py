from lsst.obs.monocam import MonocamIsrTask
config.isr.retarget(MonocamIsrTask)
# Configs to get going.
config.isr.doDark = False
config.isr.doBias = False
config.isr.doFlat = False
config.isr.doFringe = False
# we don't have astrometry_net data (yet) so astrom and photo cal are impossible
config.doCalibrate = False
