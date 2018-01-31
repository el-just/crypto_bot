# def update_cross (self):
#     if self._current_tick.at['trend'] == self._current_tick.at['avg']:
#         self._cross = self._current_tick
#     elif self._current_tick.at['avg'] < self._current_tick.at['trend']:
#         prev_tick = self._frame.iloc[self._frame.index.get_loc(self._current_tick.name) - 1]
#         if prev_tick.at['avg'] > prev_tick.at['trend']:
#             self._cross = self._current_tick
#     elif self._current_tick.at['avg'] > self._current_tick.at['trend']:
#         prev_tick = self._frame.iloc[self._frame.index.get_loc(self._current_tick.name) - 1]
#         if prev_tick.at['avg'] < prev_tick.at['trend']:
#             self._cross = self._current_tick 