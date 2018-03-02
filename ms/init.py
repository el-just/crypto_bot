import asyncio
import jinja2
import aiohttp_jinja2

import hashlib
import base64
from cryptography import fernet

from aiohttp import web
from routing import routes

app = web.Application()

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

for route in routes:
	app.router.add_route(route['method'], route['path'], route['handler'], name=route['name'])

web.run_app(app, host='127.0.0.1', port=8080)