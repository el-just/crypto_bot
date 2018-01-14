import os
import datetime
import time
import traceback

class Logging ():
    @staticmethod
    def log_error (error):
        try:
            f = open ('./logs/error.log', 'a+')
        except IOError as e:
            os.makedirs('logs')
            f = open ('./logs/error.log', 'w+')
        
        f.write ('{0}: {1}\n{2}'.format(datetime.datetime.now().isoformat(), str(error), str(traceback.format_exc())))
        f.close ()

        self.log_info ('ERROR::{}\n'.format(str(error)))

    @staticmethod
    def log_info (message):
        try:
            f = open ('./logs/info.log', 'a+')
        except IOError as e:
            os.makedirs('logs')
            f = open ('./logs/info.log', 'w+')
        
        f.write ('{0}:\n\t{1}\n'.format(datetime.datetime.now().isoformat(), message))
        f.close ()