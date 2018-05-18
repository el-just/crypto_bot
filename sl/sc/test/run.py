import os
import sys
import platform

delimiter = '/' if platform.system() == 'Linux' else '\\'

sc_path = delimiter.join(
        os.path.dirname(os.path.abspath(__file__)).split(delimiter)[:-2])
sys.path.append(sc_path)

common_path = delimiter.join(
        os.path.dirname(os.path.abspath(__file__)).split(delimiter)[:-1])
sys.path.append(common_path)

import asyncio
from common import Logger
import pandas as pd

#from exchanges import Yobit

#try:
#    loop = asyncio.get_event_loop()
#    loop.run_until_complete(asyncio.gather(*Yobit().run()))
#    loop.run_forever()
#except Exception as e:
#    Logger.log_error (e)

ticks = pd.DataFrame(
        data=[
            ['bitfinex', 'xrp_btc', '12'],
            ['binance', 'btc_usd', '10'],
            ['bitfinex', 'neo_usd', '11'],],
        columns=['exchange', 'market', 'price'],)

new_ticks = pd.DataFrame(
        data=[
            ['binance', 'btc_usd', '10'],
            ['bitfinex', 'xrp_btc', '13'],
            ['bittrex', 'neo_usd', '11'],],
        columns=['exchange', 'market', 'price'],)

resulted = pd.concat([ticks, new_ticks]).drop_duplicates().reset_index(drop=True)
diff = resulted.iloc[ticks.shape[0]:, :]
print(diff)
idx = [max(group) for group in resulted.groupby(['exchange', 'market']).groups.values()]
print(pd.concat([ticks, new_ticks]).groupby(list(ticks.columns)).groups.values())
print(pd.concat([ticks, new_ticks]).drop_duplicates())
print(resulted.reindex(idx))
