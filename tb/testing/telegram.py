from abstract.telegram import Telegram as ATelegram

class Telegram  (ATelegram):
	_commands = []

	def __init__ (self):
        self.log_info = Logging.log_info
        self.log_error = Logging.log_error