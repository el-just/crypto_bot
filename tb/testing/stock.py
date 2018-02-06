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

    def __init__ (self, source='csv'):
        super().__init__()
        self.log_info = Logging.log_info
        self.log_error = Logging.log_error

        self._web_socket.set_source (source)
        self._web_socket.set_storage (self._storage)
        self._storage.set_source (source)