import json

import asyncio
import websockets

# CHANNEL_ID  integer Channel ID
# BID float   Price of last highest bid
# BID_SIZE    float   Size of the last highest bid
# ASK float   Price of last lowest ask
# ASK_SIZE    float   Size of the last lowest ask
# DAILY_CHANGE    float   Amount that the last price has changed since yesterday
# DAILY_CHANGE_PERC   float   Amount that the price has changed expressed in percentage terms
# LAST_PRICE  float   Price of the last trade.
# VOLUME  float   Daily volume
# HIGH    float   Daily high
# LOW float   Daily low

async def connect():
    async with websockets.connect('wss://api.bitfinex.com/ws') as websocket:
        await websocket.send(json.dumps({"event":"subscribe", "channel":"ticker", "pair":"BTCUSD"}))
        while True:
            f = open ('../data/stream.s', 'a')
            f.write (str(await websocket.recv())+'\n')
            f.close ()

loop = asyncio.get_event_loop()
loop.run_until_complete(connect())
loop.close()