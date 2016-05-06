from lsst.obs.monocam.ingest import MonocamParseTask, HackParseTask, MonocamRegisterTask
config.register.retarget(MonocamRegisterTask)  # Hack the visit numbers
config.register.columns = {
    'visit': 'int',
    'basename': 'text',
    'filter': 'text',
    'date': 'text',
    'expTime': 'double',
    'ccd': 'int',
    'object': 'text',
}
config.register.visit = config.register.columns.keys()
config.allowError = True  # Errors tend to happen a lot with this camera...

if False:  # For lab data
    config.parse.retarget(MonocamParseTask)
    config.parse.hdu = 1
    config.parse.translation = {
        'date': 'DATE-OBS',
        'expTime': 'EXPTIME',
        'object': 'IMGTYPE',
    }
    config.parse.translators = {
        'visit': 'translate_visit',
        'ccd': 'translate_ccd',
        'filter': 'translate_filter',
    }
    config.parse.defaults = {
        'object': "UNKNOWN",
    }
else:  # For sky data
    config.parse.retarget(HackParseTask)


