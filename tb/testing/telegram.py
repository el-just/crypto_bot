from abstract.telegram import Telegram as ATelegram
from testing.logging import Logging

class Telegram  (ATelegram):
    def __init__ (self):
        self.log_info = Logging.log_info
        self.log_error = Logging.log_error