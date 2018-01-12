class Defines ():
    #for traiding in days
    REQUIRED_PERIOD = 90

    #interval in seconds which assuming as miss
    MISS_PERIOD = 600

    #default gap between ticks in seconds
    TICK_PERIOD = 60

    #available gap for rest request
    AVAILABLE_GAP = 59940

    #requests per minute
    REST_REQUEST_LIMIT = 10

    #available assets
    SYMBOLS = ['usd', 'btc', 'eth', 'ltc', 'etc', 'rrt', 'zec', 'xmr', 'dsh', 'xrp', 'iot', 'eos', 'san', 'omg', 'bch', 'neo', 'etp', 'qtm', 'avt', 'edo', 'btg', 'dat', 'qsh', 'yyw', 'gnt', 'snt', 'bat', 'mna', 'fun', 'zrx', 'tnb', 'spk']

    #TODO: убрать в базу
    WITHDRAWAL_FEES = [5.0, 0.0005, 0.01, 0.001, 0.01, '', 0.001, 0.04, 0.01, 0.02, None, 0.1, 0.1, 0.1, 0.0001, None, 0.01, 0.01, 0.5, 0.5, None, 1.0, None, None, '', '', '', '', '', '', '', '']

    #The minimum order size is 0.01 for BTC and ZEC and 0.1 for all other cryptocurrencies    
    def MINIMUM_ORDER_SIZE (self, symbol):
        return 0.01 if symbol in ('btc', 'zec') else 0.1   

DEFINES = Defines ()