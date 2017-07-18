const Table = require('../table.js');
const Format = require ('../format.js');
const Poloniex = require ('../../poloniex/poloniex.js');

var
	table_format = new Format ({
		"names": [
			"modify_date",
            "modify_time",
            
            "base_name",
            "quote_name",

            "close_bid",
            "lowest_ask",
            "highest_bid",

            "base_value",
            "quote_value",

            "is_frozen"
		],
		"types": [
			"Date",
			"DateTime",
			"Enum16",
			"Enum16",
			"Float64",
			"Float64",
			"Float64",

			"Float64",
			"Float64",

			"UInt8"
		]});

currencies_data_source = new DataSource (Poloniex.getAvailableCurrencies ());

table_format.setEnumSource ('base_name', currencies_data_source);
table_format.setEnumSource ('quote_name', currencies_data_source);

module.exports = new Table ('stock_frames', table_format);
