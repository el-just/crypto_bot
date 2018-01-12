import datetime
import time
import traceback

class Logging ():
    def log_error (self, error):
        f = open ('./logs/error.log', 'a+')
        f.write ('{0}: {1}\n{2}'.format(datetime.datetime.now().isoformat(), str(error), str(traceback.format_exc())))
        f.close ()

    def log_info (self, message):
        f = open ('./logs/info.log', 'a+')
        f.write ('{0}:\n{1}'.format(datetime.datetime.now().isoformat(), message))
        f.close ()
