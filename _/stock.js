const autobahn = require ('autobahn');
const data_base = require ('./data_base');

module.exports = function () {
	var
		_data_base = new data_base (),
		_listener = function () {},
		_connection = new autobahn.Connection({
	        url: 'wss://api.poloniex.com',
	        realm: 'realm1'
	    });

    _connection.onopen = function (session) {
        session.subscribe('ticker', function (pure_data) {
			var
				data = {
					'tick_date': undefined,
				    'tick_time': undefined,
				    
				    'base_name': undefined,
				    'quote_name': undefined,

				    'close_bid': undefined,
				    'lowest_ask': undefined,
				    'highest_bid': undefined,

				    'base_value': undefined,
				    'quote_value': undefined,

				    'is_active': undefined
				},
				current_time = new Date ();

			data['tick_date'] = current_time;
			data['tick_time'] = current_time;

			for (var i = 0; i < pure_data.length; i ++) {
				switch (i) {
					case 0:
						data['base_name'] = pure_data[i].split('_')[0];
						data['quote_name'] = pure_data[i].split('_')[1];
					case 1:
						data['close_bid'] = pure_data[i];
					case 2:
						data['lowest_ask'] = pure_data[i];
					case 3:
						data['highest_bid'] = pure_data[i];
					case 4:
					case 5:
						data['base_value'] = pure_data[i];
					case 6:
						data['quote_value'] = pure_data[i];
					case 7:
						data['is_active'] = Math.abs(pure_data[i]-1);
				}
			}

			_data_base.insert ('market_ticks', data).then (_listener);
        });
    }

    _connection.onclose = function (reason, details) {
        console.log('Websocket connection closed');
        console.log(reason);
        console.log(details);
    }

    _connection.open();

/*------------------------------------------------------------*/

	this.listen = function (listener) {
		_listener = listener;
	}

	this.get_ticker_frame ();
};

/*
full_sequence:
	currency_pair
	last
	lowest_ask
	highest_bid
	percent_change
	base_volume
	quote_volume
	is_frozen
	24_hr_high
	24_hr_low 
*/