from lsst.obs.monocam.ingest import MonocamParseTask, MonocamRegisterTask
config.parse.retarget(MonocamParseTask)
config.register.retarget(MonocamRegisterTask)

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
