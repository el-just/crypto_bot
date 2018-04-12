import asyncio

from common.logger import Logger
from web_server import WebServer
from stream_listener import StreamListener

sl = StreamListener()
ws = WebServer(stream=sl)

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(sl.run(), ws.run()))
    loop.close()
except Exception as e:
    Logger.log_error (e)
