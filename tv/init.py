import asyncio

from common.logger import Logger
from web_server import WebServer

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(WebServer().run())
    loop.close()
except Exception as e:
    Logger.log_error (e)
