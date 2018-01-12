import time
import datetime

from aioch import Client

from abstract.logging import Logging
from stocks.bitfinex.defines import DEFINES

class Storage (Logging):
    _socket = Client ('localhost')

    def get_sql (self, name):
        with open('./stocks/bitfinex/sql/'+name+'.sql') as f:
            sql = f.read()

        return sql

    #TODO: две нахер не нужны
    async def insert_tick (self, tick):
        await self._socket.execute ('''INSERT INTO tb.ticker (tick_date, tick_time, base, quot, close, volume) VALUES''', [{
            'tick_date': datetime.datetime.fromtimestamp(tick.at['timestamp']),
            'tick_time': datetime.datetime.fromtimestamp(tick.at['timestamp']),
            'base': tick.at['base'],
            'quot': tick.at['quot'],
            'close': tick.at['close'],
            'volume': tick.at['volume']
            }])

    async def insert_tick_frame (self, tick_frame):
        rows = []
        for idx, tick in tick_frame.iterrows():
            rows.append ({
                'tick_date': datetime.datetime.fromtimestamp(tick.at['timestamp']),
                'tick_time': datetime.datetime.fromtimestamp(tick.at['timestamp']),
                'base': tick.at['base'],
                'quot': tick.at['quot'],
                'close': tick.at['close'],
                'volume': tick.at['volume']
                })

        self.log_info ('Insert to clickhouse request:\n\t{0}'.format(str(tick_frame.shape)))
        await self._socket.execute ('''INSERT INTO tb.ticker (tick_date, tick_time, base, quot, close, volume) VALUES''', rows)

    # TODO: разобраться с этим дерьмом
    async def get_missing_periods (self, period):
        missing_periods_sql = self.get_sql ('missing_periods')
        available_data = await self._socket.execute (missing_periods_sql.format(base='btc', quot='usd', start=period['start'], end=period['end'], default_miss_time=DEFINES.MISS_PERIOD))
        periods = []
        if len (available_data) > 0:
            #если последняя доступная дата периода слишком поздняя, то нужно достать все что раньше, до доступной даты минус период тика
            if time.mktime(available_data[0][0].timetuple()) - period['start'] > DEFINES.MISS_PERIOD:
                periods.append ({
                    'start': period['start'],
                    'end': time.mktime(available_data[0][0].timetuple()) - DEFINES.TICK_PERIOD
                    })

            #посмотрим есть ли пропуски
            for idx in range(2,len(available_data)):
                periods.append ({
                    'start':time.mktime(available_data[idx][0].timetuple()) - int(available_data[idx][3]),
                    'end':time.mktime(available_data[idx][0].timetuple()) - DEFINES.TICK_PERIOD
                    })
            
            if period['start'] - time.mktime(available_data[1][0].timetuple()) > DEFINES.MISS_PERIOD:
                periods.append ({
                    'start': time.mktime(available_data[1][0].timetuple())+DEFINES.TICK_PERIOD,
                    'end': period['start']
                    })
        else:
            periods.append ({'start': period['start'], 'end': period['start']})

        return periods