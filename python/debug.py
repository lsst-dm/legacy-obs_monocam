import sys
try:
    import lsstDebug

    print "Importing debug settings..."
    def DebugInfo(name):
        di = lsstDebug.getInfo(name)
        if name in (
            "lsst.meas.astrom.astrometry",
            "lsst.meas.astrom.matchOptimisticB",
            "lsst.meas.astrom.anetAstrometry",
            "lsst.meas.astrom.anetBasicAstrometry",
            ):
            di.display = 3
            di.showLinear = True
            di.verbose = True
            di.frame = 1
            di.frame1 = 1
            di.frame2 = 2
            di.frame3 = 3
            di.pause = True
            di.scatterPlot = 2
            di.displaySources = True
        return di

    lsstDebug.Info = DebugInfo

except ImportError:
    print >> sys.stderr, "Unable to import lsstDebug; not setting display intelligently"
