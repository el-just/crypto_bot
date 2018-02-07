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
    _wallet_notify = None

    _web_connection = WEBConnection ()
    _telegram = Telegram ()

    _storage = Storage ()
    _rest_socket = RESTSocket ()
    _web_socket = WEBSocket ()
    _traider = Traider ()

    _commands = ['balance']
    _actions = ['process_balance_command']

    def __init__ (self):
        self._telegram.add_command_action (self.process_command)
        self._web_socket.add_tick_action (self.process_tick)
        self._web_socket.add_wallet_action (self.process_wallet_update)
        self._web_socket.add_order_action (self.process_order_update)
        self._traider.set_stock (self)

    async def process_tick (self, tick):
        try:
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
                await self._telegram.send_message ('thx')
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

            if self._wallet_notify is None or self._wallet_notify.day != datetime.datetime.now().day:
                if self._wallet.loc['btc'].at['balance'] == 0.:
                    self._wallet_notify = datetime.datetime.now()
                    await self._telegram.send_message (self._wallet)
        except Exception as e:
            self.log_error (e)

    async def process_order_update (self, message):
        try:
            #TODO: may be some race in future with wallet
            if message[2][5].lower() == 'executed':
                if float(message[2][2]) < 0:
                    self._traider._position = None
                else:
                    self._traider._position.at['state'] = 'done'
            elif message[2][5].lower() == 'canceled':
                raise Warning ('Order canceled {}'.format(str(message)))

            self.log_info ('Order update: {0}'.format (str(message)))
        except Exception as e:
            self.log_error (e)
    
    async def place_order (self, market=None, value=None, side=None):
        try:
            await self._rest_socket.place_order (market=market, value=value, side=side)
        except Exception as e:
            self.log_error (e)

    async def process_balance_command ():
        try:
            await self._telegram.send_message (await self._rest_socket.get_balances())
        except Exception as e:
            self.log_error (e)

    def run (self):
        return asyncio.gather(
            self._telegram.run (),
            self._web_socket.run(),
            self._traider.run ()
            )