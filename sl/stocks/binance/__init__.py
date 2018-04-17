import pandas as pd

from common import Logger
from common import formats
from stocks.binance.socket import Socket

class Binance ():
    name = 'binance'

    __socket = None
    __stream = None

    def __init__(self, stream=None):
        self.__socket = Socket ()
        self.__stream = stream

    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            exchange_info = await self.__socket.exchange_info()
            for market_data in exchange_info['symbols']:
                if market_data['status'].lower() == 'trading':
                    market = pd.Series(
                            data=[None, None, None, None, None],
                            index=formats.market,)

                    market.at['stock'] = self.name
                    market.at['base'] = market_data['baseAsset'].lower()
                    market.at['quot'] = market_data['quoteAsset'].lower()

                    for limit in market_data['filters']:
                        if limit['filterType'].lower() == 'lot_size':
                            market.at['trade_min'] = limit['minQty']
                            market.at['trade_max'] = limit['maxQty']
                    market.name = market.at['base'] + '-' + market.at['quot']

                    markets = markets.append(market)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets

    async def run(self):
        async for tick in self.__socket.run():
            if self.__stream is not None:
                await self.__stream.publish(tick)
