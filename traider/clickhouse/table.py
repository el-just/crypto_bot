from base.table import Table as BaseTable
from clickhouse.clickhouse import Clickhouse

class Table (BaseTable):
    socket = None

    def __init__ (self, db_name, tbl_name):
        super (Table, self).__init__()
        print ('init clickhouse table')
        socket = Clickhouse (db_name = db_name)

    def __getitem__ (self, key):
    	pass