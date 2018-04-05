import asyncio
import websockets

from common.logger import Logger

async def resolve_message (message):
    try:
        Logger.log_info(message)
    except Exception as e:
        Logger.log_error(e)

async def listen ():
    try:
        async with websockets.connect('ws://127.0.0.1:8765') as websocket:
            await websocket.send('ping')
            async for message in websocket:
                await resolve_message(message)
    except Exception as e:
        Logger.log_error(e)

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(listen())
    loop.close()
except Exception as e:
    Logger.log_error (e)
