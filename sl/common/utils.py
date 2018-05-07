import ast
import re
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
    except Exception as e:
        Logger.log_error(e)

    finally:
        return parsed_data

def to_pandas(data):
    if isinstance(data, dict):
        return pd.Series()

def stringify_data(data):
    if isinstance(data, (pd.Series, pd.DataFrame)):
        return data.to_csv()
    else:
        return str(data)
