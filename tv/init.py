from aiohttp import web
import jinja2
import aiohttp_jinja2

from routing import routes

async def on_shutdown(app):
    for ws in app['websockets']:
        await ws.close(code=1001, message='Server shutdown')

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

app.on_cleanup.append(on_shutdown)
app['websockets'] = []

web.run_app(app, host='127.0.0.1', port=8080)
