import pandas as pd
from common import View

class PriceFrame(View):
    def _transform_state(self, state, data):
        new_state = state

        if isinstance(data, pd.Series):
            price_row = pd.Series(
                    data=[data.at['price']],
                    index=[data.at['exchange']],
                    name=data.at['market'],)
            new_state = price_row.combine_first(state)

        return new_state
