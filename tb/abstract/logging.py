import datetime
import time
import traceback

class Logging ():
    @staticmethod
    def log_error (error):
        f = open ('./logs/error.log', 'a+')
        f.write ('{0}: {1}\n{2}'.format(datetime.datetime.now().isoformat(), str(error), str(traceback.format_exc())))
        f.close ()

    @staticmethod
    def log_info (message):
        f = open ('./logs/info.log', 'a+')
        f.write ('{0}:\n\t{1}\n'.format(datetime.datetime.now().isoformat(), message))
        f.close ()

def async_error_log (func):
    async def func_wrapper(*args, **kwargs):
        try:
            return await func (*args, **kwargs)
        except Exception as e:
            Logging.log_error (e)
    
    return func_wrapper