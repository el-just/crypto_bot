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
import pandas as pd
from buf import Buffer
from t_test import test

#from exchanges import Yobit

#try:
#    loop = asyncio.get_event_loop()
#    loop.run_until_complete(asyncio.gather(*Yobit().run()))
#    loop.run_forever()
#except Exception as e:
#    Logger.log_error (e)

a = Buffer('new')
a.a = 1
print(a.a)
test()
