from base.table import Table as BaseTable
from clickhouse.clickhouse import Clickhouse

class Table (BaseTable):
    storage = Clickhouse ('traider')

    def __init__ (self, tbl_name):
        super (Table, self).__init__()
        print ('init clickhouse table')

        print(self.storage.db_exists ('traider'))