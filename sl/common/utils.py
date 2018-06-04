import ast
import json
import datetime

import pandas as pd

from common.logger import Logger

def parse_data(data):
    parsed_data = None

    try:
        if data is not None and type(data) == str:
            data = data.replace (': null', ': None')
            data = data.replace (':null', ':None')
            data = data.replace (': undefined', ': None')
            data = data.replace (':undefined', ':None')
            data = data.replace (': true', ': True')
            data = data.replace (':true', ':True')
            data = data.replace (': false', ': False')
            data = data.replace (':false', ':False')
            parsed_data = ast.literal_eval(data)

        if isinstance(data, dict):
            pd_item = dict_to_pandas(data)
            parsed_data = pd_item if pd_data is not None else parsed_data
    except Exception as e:
        Logger.log_error(e)

    finally:
        return parsed_data

def pandas_to_dict(data):
    shape = data.shape
    data = json.loads(data.to_json(orient='split'))
    data['shape'] = shape

    return data

def dict_to_pandas(data):
    pd_item = None

    if {'index', 'columns', 'data'}.issubset(set(data.keys())):
        if 'shape' in data.keys():
            del data['shape']
        pd_item = pd.DataFrame(**data)
    elif {'index', 'name', 'data'}.issubset(set(data.keys())):
        pd_item = pd.Series(**data)

    return pd_item

def stringify_data(data):
    if isinstance(data, (pd.Series, pd.DataFrame)):
        data = pandas_to_dict(data)
        return json.dumps(data)
    else:
        return str(data)

def get_nonce():
    return str(int(datetime.datetime.now().timestamp()*1000))
