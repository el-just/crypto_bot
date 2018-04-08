import ast
from common.logger import Logger

def parse_data (data):
    parsed_data = None

    try:
        if data is not None and type(data) == str:
            data = data.replace ('null', 'None')
            data = data.replace ('undefined', 'None')
            data = data.replace ('true', 'True')
            data = data.replace ('false', 'False')
            parsed_data = ast.literal_eval(data)
    except Exception as e:
        Logger.log_error (e)

    return parsed_data

def stringify_data(data):
    return str(data.values)
