"""
Monocam-specific overrides for RunIsrTask
"""
import os.path

from lsst.utils import getPackageDir
from lsst.obs.monocam.monocamIsrTask import MonocamIsrTask

obsConfigDir = os.path.join(getPackageDir("obs_monocam"), "config")

config.isr.retarget(MonocamIsrTask)
config.isr.load(os.path.join(obsConfigDir, "isr.py"))
