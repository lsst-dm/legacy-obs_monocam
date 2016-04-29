from lsst.pipe.tasks.ingest import ParseTask

class MonocamParseTask(ParseTask):
    CCD = 0                     # Monocam's one true CCD number

    def __init__(self, *args, **kwargs):
        super(ParseTask, self).__init__(*args, **kwargs)

    def translate_ccd(self, md):
        """Return the CCD number"""
        return self.CCD

