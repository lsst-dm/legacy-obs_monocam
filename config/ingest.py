from lsst.obs.monocam.ingest import MonocamParseTask
config.parse.retarget(MonocamParseTask)

config.parse.hdu = 1

config.parse.translation = {'visit'  : 'EXPNUM',
                            'taiObs' : 'DATE-OBS', 
                            'dateObs' : 'DATE-OBS', 
                            'expTime': 'EXPTIME',
                            'filter' : 'FILTER',
                            'object' : 'IMGTYPE',
			    'date'   : 'DATE',
                          }

config.parse.translators = {
    'ccd': 'translate_ccd',
                          }


config.register.columns = {'visit':    'int',
                           'filter':   'text',
                           'date':     'text',
                           'dateObs':   'text',
                           'expTime':  'double',
                           'ccd':      'int',
                           'object':   'text',
                           #'hdu':      'int',
                         }
