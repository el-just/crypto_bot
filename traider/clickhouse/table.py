from base.table import Table as BaseTable

class Table (BaseTable):
    def __init__ (self):
        super (Table, self).__init__()
        print ('init clickhouse table')