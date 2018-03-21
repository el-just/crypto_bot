from aiohttp import web
import aiohttp_jinja2

class Login (web.View):
    @aiohttp_jinja2.template('login.html')
    async def get(self):
        return {}
