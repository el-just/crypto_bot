import pandas as pd
from common import Logger

class View():
    name = None
    state = None
    diff = None

    def __init__(self):
        self.state = pd.DataFrame()

    def __get_diff(self, old, new):
        diff = pd.DataFrame()
        concat = old.append(new)
        if not concat.empty and concat.shape[0] > 1:
            concat = concat.drop_duplicates()

        if old.shape[0] != concat.shape[0]:
            pre_diff = concat.iloc[old.shape[0]:, :]

            for idx, row in pre_diff.iterrows():
                for column in row.index.values:
                    if idx in old.index and column in old.columns:
                        if row.at[column] == old.loc[idx, :].at[column]:
                            row.at[column] = None

            diff = pre_diff.dropna(how='all')

        if diff.empty:
            diff = None

        return diff

    def update(self, data):
        new_state = self._transform_state(self.state.copy(), data)
        self.diff = self.__get_diff(self.state, new_state)
        self.state = new_state

    def _transform_state(self, data): pass
