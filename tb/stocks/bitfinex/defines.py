#for traiding in days
REQUIRED_PERIOD = 90

#default gap between ticks in seconds
TICK_PERIOD = 60

#available assets
SYMBOLS = ['usd', 'btc', 'eth', 'ltc', 'etc', 'rrt', 'zec', 'xmr', 'dsh', 'xrp', 'iot', 'eos', 'san', 'omg', 'bch', 'neo', 'etp', 'qtm', 'avt', 'edo', 'btg', 'dat', 'qsh', 'yyw', 'gnt', 'snt', 'bat', 'mna', 'fun', 'zrx', 'tnb', 'spk']

#The minimum order size is 0.01 for BTC and ZEC and 0.1 for all other cryptocurrencies
def MINIMUM_ORDER_SIZE (symbol):
    return 0.01 if symbol in ('btc', 'zec') else 0.1

#TODO: убрать в базу
WITHDRAWAL_FEES = [5.0, 0.0005, 0.01, 0.001, 0.01, '', 0.001, 0.04, 0.01, 0.02, None, 0.1, 0.1, 0.1, 0.0001, None, 0.01, 0.01, 0.5, 0.5, None, 1.0, None, None, '', '', '', '', '', '', '', '']