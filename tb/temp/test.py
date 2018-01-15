'''
BotFather, [12.01.18 17:14]
Done! Congratulations on your new bot. You will find it at t.me/ej_dev_tb_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

Use this token to access the HTTP API:
509542441:AAF3UMLVxRKLD1jT9W9IRc6fcFMnT7pBFTk

https://api.telegram.org/bot509542441:AAF3UMLVxRKLD1jT9W9IRc6fcFMnT7pBFTk/sendMessage?chat_id=276455649&text=wtf

For a description of the Bot API, see this page: https://core.telegram.org/bots/api

===========


{"event":"info","version":1.1}
{"event":"subscribed","channel":"ticker","chanId":1,"pair":"BTCUSD"}
[1,14572,64.62977371,14583,48.78065323,-779,-0.0507,14585,63518.10813398,15479,13755]
{"event":"subscribed","channel":"ticker","chanId":3,"pair":"ETHUSD"}
[3,1191.4,156.95650816,1192.4,919.04951283,55.2,0.0486,1191.6,349747.62944201,1250,965.18]
{"event":"subscribed","channel":"ticker","chanId":10,"pair":"LTCUSD"}
[10,244.96,1682.60984158,245.55,869.76850418,-11.33,-0.0442,244.96,319916.10135213,259.26,230.18]
{"event":"subscribed","channel":"ticker","chanId":19,"pair":"ETCUSD"}

'''

import datetime
import time
import urllib.parse
import asyncio
import aiohttp
import pandas as pd

PYTHONASYNCIODEBUG=1



async def execute (query):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:8123/', data=query) as resp:
            text = await resp.text()
            print (text)
            return text

ioloop = asyncio.get_event_loop()
ioloop.run_until_complete(execute ('SELECT 1'))
ioloop.close()