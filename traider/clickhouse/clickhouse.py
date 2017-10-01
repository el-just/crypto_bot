import http.client

class Clickhouse ():
    db_name = None
    db_port = 8123
    def __init__ (self, db_name):
        self.db_name = db_name

    def request (self, request):
        query = '''
            use {db_name}

            {request}
            '''.format (db_name=self.db_name)

        connect = http.client.HTTPConnection('localhost', self.db_port)
        connect.request ('POST', '/', query)
        response = connect.getresponse ()

        return response.read()

    def db_exists (self, db_name):
        query = '''
            select
                count(name)
            from
                system.databases
            where name='{db_name}'
            format CSV
            '''.format (db_name=db_name)

        connect = http.client.HTTPConnection('localhost', self.db_port)
        connect.request ('POST', '/', query)
        response = connect.getresponse ()

        return response.read()
