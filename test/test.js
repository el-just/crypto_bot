var
   fs = require('fs');

function read (storage) {
   return new Promise (function (resolve, reject) {
      fs.readFile('./BTC_GAME.d', 'utf8', function (err,data) {
         if (err) {
            console.log(err);
            reject (err);
         }

         resolve (JSON.parse (data));
      });
   }); 
}

function convert (pure_ticker_data) {
	var
		ticker_data = [];

	for (tick of pure_ticker_data) {
		ticker_data.push ({
			'tick_date': new Date (tick.date*1000),
		   'tick_time': new Date (tick.date*1000),
		    
		   'base_name': 'BTC',
		   'quote_name': 'GAME',

		   'close_bid': tick.close,
		   'lowest_ask': tick.low,
		   'highest_bid': tick.high,

		   'base_value': tick.volume,
		   'quote_value': tick.quoteVolume,

		   'is_active': 1
		})
	}

	return ticker_data;
}

read ().then ((pure_ticker_data) => {
	var i;

	ticker_data = convert (pure_ticker_data)

	
	edge_peak = {
		idx: 0,
		value: ticker_data[0].close_bid
	}

	last_peak = {
		idx: 0,
		value: ticker_data[0].close_bid
	}

	

	for (i=1; i<ticker_data.length; i++) {

		if (ticker_data[i].close_bid > ticker_data[i-1].value) {
			// вверх
		}
		else if (ticker_data[i].close_bid < ticker_data[i-1].value) {
			//вниз

		}
		ticker_data[i]
	}

	console.log (ticker_data);
});