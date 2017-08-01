const Clickhouse = require ('../blocks/data/storage/clickhouse/clickhouse.js');

var 
    currencies_fromat = {
        "modify_date": "Date",
        "modify_time": "DateTime",
        "name": "String",
        "full_name": "String",
        "id": "UInt32",
        "tax_fee": "Float64",
        "min_conf": "UInt32",
        "base_address": "String",
        "is_active": "UInt8",
        "imprint": "String"
    },
    frames_format = null;


const data_base = new Clickhouse ({
    name: 'traider',
    tables: {
        currencies: currencies_format,
        frames: frames_format
    }
});

module.exports = {
    init: data_base.deploy
};