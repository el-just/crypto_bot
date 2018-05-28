import pandas as pd
from common import View
from common import Logger

class PriceFrame(View):
    def _transform_state(self, state, data):
        new_state = state
        Logger.log_info(data)

        if isinstance(data, pd.Series):
            price_row = pd.Series(
                    data=[data.at['price']],
                    index=[data.at['exchange']],
                    name=data.at['market'],)
            price_frame = pd.DataFrame().append(price_row)
            new_state = price_frame.combine_first(state)

        return new_state
