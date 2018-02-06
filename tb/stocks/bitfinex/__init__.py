import time
import datetime
import asyncio
import pandas as pd
import numpy as np

from abstract.logging import Logging
from abstract.web_connection import WEBConnection
from abstract.telegram import Telegram
from stocks.bitfinex.defines import DEFINES

from stocks.bitfinex.storage import Storage
from stocks.bitfinex.rest_socket import RESTSocket
from stocks.bitfinex.web_socket import WEBSocket
from stocks.bitfinex.traider import Traider

class Bitfinex (Logging):
    _wallet = None
    _wallet_notified = False

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
        self._web_socket.add_wallet_action (self.process_wallet_update)
        self._traider.set_stock (self)

    async def process_tick (self, tick):
        try:
            if tick.name.hour == 0 and self._wallet_notified is False:
                self._wallet_notified = True
                await self._telegram.send_message (self._wallet)
            elif tick.name.hour != 0 and self._wallet_notified is True:
                self._wallet_notified = False

            await self._storage.insert_ticks (tick)
            await self._traider.resolve (tick)
        except Exception as e:
            self.log_error (e)

    async def process_command (self, command):
        try:
            if command in self._commands:
                await self._telegram.send_message ('command_accepted')
                await self.__class__.__dict__[ self._actions[self._commands.index(command)] ](self)
            elif command == 'nice' or command == 'gj':
                await self._telegram.send_message ('tnx')
        except Exception as e:
            self.log_error (e)

    async def process_wallet_update (self, message):
        try:
            if message[1] == 'ws':
                self._wallet = pd.DataFrame (data=[], columns=['balance'])
                for row in message[2]:
                    currency = pd.Series(data=[row[2]], index=['balance'])
                    currency.name = row[1].lower()
                    self._wallet = self._wallet.append (currency)
            elif message[1] == 'wu':
                self._wallet.loc[message[2][1].lower()] = message[2][2]
        except Exception as e:
            self.log_error (e)
    
    async def place_order (self, base=None, quot=None, value=None):
        try:
            # TODO web_socket order =====>
            await self.web_socket.place_order (base=base, quot=quot, value=value)
        except Exception as e:
            self.log_error (e)

    def run (self):
        return asyncio.gather(
            self._telegram.run (),
            self._web_socket.run(),
            self._traider.run ()
            )