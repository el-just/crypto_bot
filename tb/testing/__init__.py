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
# [0,"wu",["exchange","BTC",0.06430686,0]]
# 2018-02-08T18:47:26.661259:
# 	Web Socket message:
# 	[0,"wu",["exchange","XRP",1000,0]]
# 2018-02-08T18:47:26.662259:
# 	Web Socket message:
# 	[0,"on",[8078837700,"XRPBTC",-696.6,-696.6,"EXCHANGE MARKET","ACTIVE",0.00009008,0.0000901,"2018-02-08T15:47:26Z",0,0,0]]
# 2018-02-08T18:47:26.663259:
# 	Order update: [0, 'on', [8078837700, 'XRPBTC', -696.6, -696.6, 'EXCHANGE MARKET', 'ACTIVE', 9.008e-05, 9.01e-05, '2018-02-08T15:47:26Z', 0, 0, 0]]
# 2018-02-08T18:47:26.663259:
# 	Web Socket message:
# 	[0,"oc",[8078837700,"XRPBTC",0,-696.6,"EXCHANGE MARKET","EXECUTED @ 0.0001(-696.6)",0.00009008,0.0000901,"2018-02-08T15:47:26Z",0,0,0]]
# 2018-02-08T18:47:26.714259:
# 	Web Socket message:
# 	[0,"te",["3374734-XRPBTC","XRPBTC",1518104846,8078837700,-696.6,0.0000901,null,null]]
# 2018-02-08T18:47:26.809259:
# 	ERROR::malformed node or string: <_ast.Name object at 0x0DC38D50>



# {'id': 8078837700, 'cid': 56846510910, 'cid_date': '2018-02-08', 'gid': None, 'symbol': 'xrpbtc', 'exchange': 'bitfinex', 'price': '0.00009008', 'avg_execution_price': '0.0000901', 'side': 'sell', 'type': 'exchange market', 'timestamp': '1518104847.0', 'is_live': False, 'is_cancelled': False, 'is_hidden': False, 'oco_order': None, 'was_forced': False, 'original_amount': '696.6', 'remaining_amount': '0.0', 'executed_amount': '696.6', 'src': 'api'}