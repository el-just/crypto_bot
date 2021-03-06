import os
import sys
import platform

delimiter = '/' if platform.system() == 'Linux' else '\\'
common_path = delimiter.join(
        os.path.dirname(os.path.abspath(__file__)).split(delimiter)[:-1])
sys.path.append(common_path)

import asyncio
from common import Logger
from web_server import WebServer

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(WebServer().run())
    loop.close()
except Exception as e:
    Logger.log_error (e)
