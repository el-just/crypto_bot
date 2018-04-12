from aiohttp import web
import jinja2
import aiohttp_jinja2

from routing import routes

class WebServer():
    __stream = None

    def __init__(self, stream=None):
        self.__stream = stream

    async def __on_shutdown(self):
        for ws in app['websockets']:
            await ws.close(code=1001, message='Server shutdown')

    async def run(self):
        app = web.Application ()
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

        app['static_root_url'] = '/static'
        app.router.add_static('/static', 'static', name='static')
        for route in routes:
            app.router.add_route(
                    route['method'],
                    route['path'],
                    route['handler'],
                    name=route['name'],)

        app.on_cleanup.append(self.__on_shutdown)
        app['websockets'] = []
        if self.__stream is not None:
            app['stock_stream'] = self.__stream

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '127.0.0.1', 8080)
        await site.start()
