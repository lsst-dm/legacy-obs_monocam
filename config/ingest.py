from lsst.obs.ctio0m9.ingest import Ctio0m9ParseTask
config.parse.retarget(Ctio0m9ParseTask)
config.parse.translation = {
    'expTime': 'EXPTIME',
    'object': 'OBJECT',
    'imageType': 'IMAGETYP',
    #'filter': 'FILTERS',
    #'visit': 'VISIT',
    'amp11':'TSEC11',
#    'amp12':'TSEC12',
}
config.parse.translators = {
    'visit': 'translate_visit',
    'ccd': 'translate_ccd',
    'amp': 'translate_amp',
    'date': 'translate_date',
    'filter': 'translate_filter',
}
config.parse.defaults = {
    'object': "UNKNOWN",
}
config.parse.hdu = 0

config.register.columns = {
    'visit': 'int',
    'basename': 'text',
    'filter': 'text',
    'date': 'text',
    'expTime': 'double',
    'ccd': 'int',
    'object': 'text',
    'imageType': 'text',
    'amp11':'text',
    'amp':'text',

    
}
config.register.visit = list(config.register.columns.keys())
