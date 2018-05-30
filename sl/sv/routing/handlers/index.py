import pandas as pd

from aiohttp import web
import aiohttp_jinja2

from common import utils
from common import Buffer
from common import Logger
import decimal

class Index (web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        ctx = decimal.Context()
        ctx.prec = 20

        exchanges_socket = Buffer('exchanges').connect()
        price_frame_view = await exchanges_socket.execute(
                'get_view',
                'price_frame',)
        await exchanges_socket.close()

        price_frame_view = price_frame_view.dropna()

        price_frame_view['gap'] = (
                price_frame_view.loc[:, 'gateio'].astype('float64')
                - price_frame_view.loc[:, 'hitbtc'].astype('float64')
                ).abs()
        price_frame_view = price_frame_view.sort_values(by='gap', ascending=False)
        price_frame_view['gap'] = price_frame_view['gap'].apply(
                lambda x: format(ctx.create_decimal(repr(x)), 'f'))
        return {'grid': utils.pandas_to_dict(price_frame_view)}
