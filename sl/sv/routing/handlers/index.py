import pandas as pd

from aiohttp import web
import aiohttp_jinja2

from common import utils
from common import Buffer

class Index (web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        price_frame_view = await Buffer('exchanges').execute(
                'get_view',
                'price_frame',)

        return {'grid': utils.pandas_as_dict(price_frame_view.state)}
