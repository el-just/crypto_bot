import time
import datetime
import pandas as pd
from io import StringIO

import aiohttp

from abstract.logging import Logging
from stocks.bitfinex.defines import DEFINES

class Storage (Logging):
    def get_sql (self, name):
        with open('./stocks/bitfinex/sql/'+name+'.sql') as f:
            sql = f.read()

        return sql

    def parse_response (self, response):
        response = None if response == '' else pd.read_csv (StringIO(response))
        self.log_info ('Clickhouse response:\n "{}"'.format (str(response)))
        return response

    async def execute (self, query):
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:8123/', data=query) as resp:
                text = await resp.text()
                return self.parse_response(text)

    async def insert_ticks (self, ticks):
        try:
            rows = []
            tick_frame = pd.DataFrame (data=[], columns=['timestamp', 'base', 'quot', 'close', 'volume'])
            tick_frame = tick_frame.append (ticks, ignore_index=True)
            
            for idx, tick in tick_frame.iterrows():
                rows.append ('''(toDate({tick_date}), toDateTime({tick_time}), '{base}', '{quot}', {close}, {volume})'''.format (
                    tick_date = int(tick.at['timestamp']),
                    tick_time = int(tick.at['timestamp']),
                    base = str(tick.at['base']),
                    quot = str(tick.at['quot']),
                    close = float(tick.at['close']),
                    volume = float (tick.at['volume'])
                    ))

            query = '''INSERT INTO tb.ticker (tick_date, tick_time, base, quot, close, volume) VALUES {values}'''.format (values=', '.join (rows))
            self.log_info ('Insert to clickhouse request:\n\t{0}\n'.format(str(tick_frame.shape)))
            await self.execute (query)
        except Exception as e:
            self.log_error (e)

    async def get_missing_periods (self, period):
        try:
            missing_periods_sql = self.get_sql ('missing_periods')
            available_data = await self.execute (missing_periods_sql.format(base='btc', quot='usd', start=period['start'], end=period['end'], default_miss_time=DEFINES.MISS_PERIOD))
            available_data.loc[:, 'tick_time'] = pd.to_timestamp[available_data.loc[:, 'tick_time']]
            print (available_data)
            raise Warning ('asd')
            periods = []
            if available_data is not None:
                #если последняя доступная дата периода слишком поздняя, то нужно достать все что раньше, до доступной даты минус период тика
                if available_data.loc[0].at['tick_time'] - period['start'] > DEFINES.MISS_PERIOD:
                    periods.append ({
                        'start': period['start'],
                        'end': available_data.loc[0].at['tick_time'] - DEFINES.TICK_PERIOD
                        })

                #посмотрим есть ли пропуски
                for idx in range(2,available_data.shape[0]):
                    periods.append ({
                        'start': available_data.loc[idx].at['tick_time'] - int(available_data.loc[idx].at['delta']) + DEFINES.TICK_PERIOD,
                        'end':available_data.loc[idx].at['tick_time'] - DEFINES.TICK_PERIOD
                        })
                
                if period['end'] - available_data.loc[1].at['tick_time'] > DEFINES.MISS_PERIOD:
                    periods.append ({
                        'start': available_data.loc[1].at['tick_time']+DEFINES.TICK_PERIOD,
                        'end': period['end']
                        })
            else:
                periods.append ({'start': period['start'], 'end': period['end']})

            return periods
        except Exception as e:
            self.log_error (e)