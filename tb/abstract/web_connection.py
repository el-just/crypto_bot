import socket

class WEBConnection ():
    _targets = [
        {'host':'8.8.8.8', 'port':53},
        {'host':'8.8.4.4', 'port':53}
        ]

    def ping (self, host=None, port=None, timeout=3):
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))

    def check (self):
        for target in self._targets:
            try:
                self.ping (host=target['host'], port=target['port'])
                return True
            except Exception as e:
                return False