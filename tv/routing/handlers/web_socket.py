from aiohttp import web, WSMsgType

class WebSocket(web.View):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        self.request.app['websockets'].append(ws)

        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    await ws.send_str('message accepted: '+str(msg.data))
            elif msg.type == WSMsgType.ERROR:
                pass

        self.request.app['websockets'].remove(ws)
        return ws
