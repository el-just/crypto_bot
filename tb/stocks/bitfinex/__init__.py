import time
import datetime
import asyncio
import pandas as pd
import numpy as np

from abstract.logging import Logging
from abstract.web_connection import WEBConnection
from stocks.bitfinex.defines import DEFINES

from stocks.bitfinex.storage import Storage
from stocks.bitfinex.rest_socket import RESTSocket
from stocks.bitfinex.web_socket import WEBSocket
from stocks.bitfinex.traider import Traider

class Bitfinex (Logging):
    # TODO: real balance
    _balance = pd.Series (data=[2000., 0.], index=['usd', 'btc'])

    _web_connection = WEBConnection ()
    _telegram = Telegram ()

    _storage = Storage ()
    _rest_socket = RESTSocket ()
    _web_socket = WEBSocket ()
    _traider = Traider ()

    _commands = []
    _actions = []

    def __init__ (self):
        self._telegram.add_command_action (self.process_command)
        self._web_socket.add_tick_action (self.process_tick)
        self._traider.set_stock (self)

    async def process_tick (self, tick):
        await self._storage.insert_ticks (tick)
        await self._traider.resolve (tick)

    async def process_command (self, command):
        if command in self._commands:
            await self.telegram.send_message ('command_accepted')
            await self.__class__.__dict__[ self._actions[self._commands.index(command)] ](self)
        elif command == 'nice':
            await self.telegram.send_message ('tnx')

    def run (self):
        return asyncio.gather(
            self._telegram.run (),
            self._web_socket.run(),
            self._traider.run ()
            )