import http.client

class Clickhouse ():
    db_name = None
    db_port = 8123
    def __init__ (self, db_name):
        self.db_name = db_name
        print ('init clickhouse socket')

    def request (self, request):
        connect = http.client.HTTPConnection('localhost', self.db_port)
        connect.request ('POST', '/', query)
        response = connect.getresponse ()

        return self.__decode_response ( pure_response=response.read() )

    def db_exists (self, db_name):
        query = '''
            select
                count(name)
            from
                system.databases
            where name='{db_name}'
            format CSV
            '''.format ( db_name=db_name )

        return True if self.request (query) is not None else False

    def __decode_response (self, pure_response):
        decoded_response = pure_response.decode ('utf8')
        decoded_response = decoded_response if decoded_response is not None and len(decoded_response) > 0 else None

        return decoded_response