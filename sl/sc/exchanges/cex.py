import datetime
import time
import hmac
import hashlib

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges import Exchange

class Cex(Exchange):
    name = 'cex'

    _key = 'LbjBXHmk3pPI2Ur4p2S3bCUSpD4'
    _pattern = 'OVelFsTeuwd5IeycU72Rp1Itj78'

    _ws_path = 'wss://ws.cex.io/ws'
    _rest_path = 'https://cex.io/api/'

######################    Exchange required   ################################
    async def _ws_auth(self):
        try:
            timestamp = int(datetime.datetime.now().timestamp())
            string = "{}{}".format(timestamp, self._key)
            signature = hmac.new(
                    self._pattern.encode(),
                    string.encode(),
                    hashlib.sha256,).hexdigest()

            await self.ws_send({
                    'e': 'auth',
                    'auth': {
                        'key': self._key,
                        'signature': signature,
                        'timestamp': timestamp,},
                    'oid': 'auth',})
        except Exception as e:
            Logger.log_error(e)

    async def _subscribe_channels(self):
        try:
            await self.ws_send({
                    "rooms": [
                        "tickers",],
                    "e": "subscribe",
                    "oid": self._get_nonce() + '_subscribe',})
        except Exception as e:
            Logger.log_error(e)

    async def _resolve_message(self, message):
        reaction = None

        try:
            message = utils.parse_data(message)
            if message.get('e', None) == 'ping':
                await self.ws_send({'e':'pong'})
            elif message.get('e', None) == 'tick':
                reaction = self.__assume_tick(message)

        except Exception as e:
            Logger.log_error(e)

        finally:
            return reaction

######################    Private    #########################################
    def __assume_tick(self, message):
        tick = None

        try:
            current_date = datetime.datetime.now()
            tick = pd.Series (
                    data=[
                        self.name,
                        int(time.mktime(current_date.timetuple()))*1000,
                        '_'.join([
                            message['data']['symbol1'].lower(),
                            message['data']['symbol2'].lower(),]),
                        message['data']['price'],],
                    index=formats.tick,
                    name=current_date,)

            Logger.log_info(tick)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick

###########################    API    ########################################
    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'currency_limits'

            stock_data = await self.rest_send(request_url)
            for market_data in stock_data['data']['pairs']:
                markets = markets.append(pd.Series(
                        data=[
                            self.name,
                            market_data['symbol1'],
                            market_data['symbol2'],
                            market_data['minLotSize'],
                            market_data['maxLotSize'],],
                        index=formats.market,
                        name='_'.join([
                            market_data['symbol1'],
                            market_data['symbol2']]),))
        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
