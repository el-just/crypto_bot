import websockets
import aiohttp
import asyncio

ETH_API_KEY = 'RHFNWQYJNFCQ8N6ISGGIN9T5AZV7I4N7ED'

async def subscribe_channels (websocket):
    await websocket.send(json.dumps({"op":"addr_sub", "addr":""}))
    pass 

async def listen(self):
    try:
        while True:
            try:
                async with websockets.connect('wss://ws.blockchain.info/inv') as websocket:
                    await subscribe_channels (websocket)
                    async for message in websocket:
                        print (message)
            except Exception as e:
                pass
    except Exception as e:
        pass

async def get_balancies (bitcoin_address):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://blockchain.info/ru/rawaddr/{bitcoin_address}'.format (bitcoin_address)) as resp:
            text = await resp.text()
            return text

async def get_eth_balancies (address):
    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={API_KEY}'.format (address=address, API_KEY=ETH_API_KEY)) as resp:
                    text = await resp.text()
                    print (text)
                    return text
            except Exception as e:
                print (e)
    except Exception as e:
        print (e)

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_eth_balancies ('0xca260106a2AF5169C17A7CD570F9d735B540eeC4'))
    loop.close()
except Exception as e:
    print (e)