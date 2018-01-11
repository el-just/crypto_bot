from aioch import Client

class Storage ():
    _socket = Client ('localhost')

    def get_sql (name):
        with open('./stocks/bitfinex/sql/'+name+'.sql') as f:
            sql = f.read()

        return sql

    # TODO: разобраться с этим дерьмом
    async def get_missing_periods (self, start=None, end=None):
        missing_periods_sql = self.get_sql ('missing_periods')
        available_data = await self._socket.execute (missing_periods_sql.format(base='btc', quot='usd', start=start, end=end))
        default_tick_period = 60
        default_miss_period = 600
        periods = []
        if len (available_data) > 0:
            #если последняя доступная дата периода слишком поздняя, то нужно достать все что раньше, до доступной даты минус период тика
            if time.mktime(available_data[0][0].timetuple()) - start > default_miss_period:
                periods.append ({
                    'start': start,
                    'end': time.mktime(available_data[0][0].timetuple()) - default_tick_period
                    })

            #посмотрим есть ли пропуски
            for idx in range(2,len(available_data)):
                periods.append ({
                    'start':time.mktime(available_data[idx][0].timetuple()) - int(available_data[idx][3]),
                    'end':time.mktime(available_data[idx][0].timetuple()) - default_tick_period
                    })
            
            if end - time.mktime(available_data[1][0].timetuple()) > default_miss_period:
                periods.append ({
                    'start': time.mktime(available_data[1][0].timetuple())+default_tick_period,
                    'end': end
                    })
        else:
            periods.append ({'start': start, 'end': end})

        return periods