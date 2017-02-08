from lsst.obs.ctio0m9.ingest import Ctio0m9ParseTask
config.parse.retarget(Ctio0m9ParseTask)
config.parse.translation = {
    'expTime': 'EXPTIME',
    'object': 'OBJECT',
    'imageType': 'IMAGETYP',
    'filter': 'FILTERS',
    #'visit': 'VISIT',
}
config.parse.translators = {
    'visit': 'translate_visit',
    'ccd': 'translate_ccd',
    'date': 'translate_date',
}
config.parse.defaults = {
    'object': "UNKNOWN",
}
config.parse.hdu = 1

config.register.columns = {
    'visit': 'int',
    'basename': 'text',
    'filter': 'text',
    'date': 'text',
    'expTime': 'double',
    'ccd': 'int',
    'object': 'text',
    'imageType': 'text',
}
config.register.visit = list(config.register.columns.keys())
