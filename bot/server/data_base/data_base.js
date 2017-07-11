const Socket = require('./socket.js');
const Table = require('./table.js');
const tables_format_path = '/dev/bot/server/data_base/tables'

function DataBase () {
	var _socket = new Socket ();

	this.name = 'ej';

	this.request = function (request) {
		console.log ('About to send request: ' + request);
		return new Promise ((resolve, reject) => {
			_socket.send (request).then ((response) => {
				resolve (response);
			});
		});
	}

	this.currencies = new Table ('currencies', {
		"names": [
	        "modify_date",
	        "modify_time",
	        "name",
	        "full_name",
	        "id",
	        "tax_fee",
	        "min_conf",
	        "deposit_address",
	        "is_disabled",
	        "is_delisted",
	        "is_frozen",
	        "imprint"
	    ],
	    "types": [
	        "Date",
	        "DateTime",
	        "String",
	        "String",
	        "UInt32",
	        "Float64",
	        "UInt32",
	        "String",
	        "UInt8",
	        "UInt8",
	        "UInt8",
	        "String"
	    ],
	    "date_field": "modify_date",
	    "key_fields": "modify_date, name, imprint"
	}, this);

	this.stock_frames = new Table ('stock_frames', {
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

			"Uint8"
		]
	}, this);
}

module.exports = new DataBase ();