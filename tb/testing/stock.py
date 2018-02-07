from stocks.bitfinex import Bitfinex
from testing.web_socket import WEBSocket
from testing.storage import Storage
from testing.traider import Traider
from testing.telegram import Telegram
from testing.logging import Logging

class Stock (Bitfinex):
    _telegram = Telegram ()
    _storage = Storage()
    _web_socket = WEBSocket()
    _traider = Traider()

    _commands = ['test_action', 'test_order']
    _actions = ['process_test_action', 'process_test_order']

    def __init__ (self, source='csv'):
        super().__init__()
        self.log_info = Logging.log_info
        self.log_error = Logging.log_error

        self._web_socket.set_source (source)
        self._web_socket.set_storage (self._storage)
        self._storage.set_source (source)

    async def process_test_action (self):
        try:
            wallets_info = await self._rest_socket.get_balances()
            await self._telegram.send_message (wallets_info)
        except Exception as e:
            self.log_error (e)

    async def process_test_order (self):
        try:
            result = await self._rest_socket.place_order (market='xrpusd', value='696.6', side='sell')
            await self._telegram.send_message (result)
        except Exception as e:
            self.log_error (e)

    async def place_order (self, market=None, value=None, side=None):
        try:
            wallet_state = None
            order_state = None

            if side == 'buy':
                balance = self._wallet.loc['usd'].at['balance'] - self._traider._position.at['price']*self._traider._position.at['expect_currency']
                wallet_state = [0,'ws',[['','btc', self._traider._position.at['expect_currency']],['','usd', balance]]]
                order_state = [0,'on',[None, 'btcusd', self._traider._position.at['expect_currency'], None, None, 'executed']]
            else:
                wallet_state = [0,'ws',[['','btc', 0.],['','usd',self._traider._position.at['expect_usd']+self._wallet.loc['usd'].at['balance']]]]
                order_state = [0,'on',[None, 'btcusd', -self._traider._position.at['expect_usd'], None, None, 'executed']]
            
            await self._web_socket._process_actions (self._web_socket._wallet_actions, wallet_state)
            await self._web_socket._process_actions (self._web_socket._order_actions, order_state)
        except Exception as e:
            self.log_error (e)