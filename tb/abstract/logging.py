import os
import datetime
import time
import traceback
import http.client

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

        Logging.log_info ('ERROR::{}\n'.format(str(error)))
        Logging.log_telegram ('ERROR::{0}: {1}\n{2}'.format(datetime.datetime.now().isoformat(), str(error), str(traceback.format_exc())[0:100]))

    @staticmethod
    def log_info (message):
        try:
            f = open ('./logs/info.log', 'a+')
        except IOError as e:
            os.makedirs('logs')
            f = open ('./logs/info.log', 'w+')
        
        f.write ('{0}:\n\t{1}\n'.format(datetime.datetime.now().isoformat(), message))
        f.close ()

    @staticmethod
    def log_telegram (message):
        params = {'chat_id': 276455649, 'text': str(message)}
        conn = http.client.HTTPSConnection ('api.telegram.org', 443)
        conn.request("GET", "/bot509542441:AAF3UMLVxRKLD1jT9W9IRc6fcFMnT7pBFTk/sendMessage?"+urllib.parse.urlencode(params))
        conn.getresponse().read().decode('utf8')
        conn.close()