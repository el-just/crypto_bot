import json
import urllib.parse

import asyncio
import aiohttp

from stocks.bitfinex.defines import DEFINES
from abstract.logging import Logging

class Telegram (Logging):
    _chat_id = 276455649
    _base_path = 'https://api.telegram.org/bot'+DEFINES.TELEGRAM+'/'
    _event = None

    _command_actions = []

    async def _process_request (self, request):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(request) as resp:
                    text = await resp.text()
                    return text
        except Exception as e:
            self.log_error (e)

    def _parse_response (self, response):
        response = json.loads (response)
        command = None
        if 'result' in response and len (response['result']) > 0:
            payload = response['result'][0]
            if self._event is None or self._event['update_id'] != payload['update_id']:
                if payload['message']['chat']['id'] == self._chat_id and 'text' in payload['message']:
                    self._event = payload
                    command = self._event['message']['text']

        return command

    def add_command_action (self, command_action):
        self._command_actions.append(command_action)

    async def send_message (self, message):
        try:
            params = {'chat_id': self._chat_id, 'text': str(message)}
            await self._process_request (self._base_path+'sendMessage?'+urllib.parse.urlencode(params))
        except Exception as e:
            self.log_error (e)

    async def get_updates (self):
        try:
            params = {'limit':1, 'offset':-1}
            response = await self._process_request (self._base_path+'getUpdates?'+(urllib.parse.urlencode(params)))

            return self._parse_response (response)
        except Exception as e:
            self.log_error (e)

    async def run (self):
        while True:
            try:
                command = await self.get_updates ()
                if command is not None:
                    if len (self._command_actions) > 0:
                        for command_action in self._command_actions:
                            await command_action (command)
                        await self.send_message ('command_procceed')
                await asyncio.sleep (1)
            except Exception as e:
                self.log_error (e)
        