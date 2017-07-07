// const http = require('http');
// const Router = require('./router.js');
// const WebSocketServer = require('./sockets/web_browser.js');
//const Poloniex = require('./poloniex/poloniex.js');
const DataBase = require('./data_base/data_base.js');

// const hostname = '0.0.0.0';
// const port = 3000;

// var
//   router = new Router ();

// const server = http.createServer((req, res) => {
//   console.log ('Request accepted');
//   router.resolveAction (req).then ((actionResult) => {
//     router.responseClient(req, res, actionResult);
//   });
// });

// server.listen(port, hostname, () => {
//   console.log(`Server running at http://${hostname}:${port}/`);
// });

// poloniex_socket.listen((ticker_data) => {
//     var param_sequence = [
//         "currencyPair",
//         "last",
//         "lowestAsk",
//         "highestBid",
//         "percentChange",
//         "baseVolume",
//         "quoteVolume",
//         "isFrozen",
//         "24hrHigh",
//         "24hrLow"
//         ];

//     ticker_data.forEach ((ticker_param, index) => {
//         console.log (param_sequence[index] + ' = ' + ticker_param);        
//     });
// });

//Poloniex.updateCurrencies();
DataBase.currencies.create();

// var
// 	fs = require('fs');

// fs.readFile('./data_base/create_table_currencies.sql', 'utf8', function (err,data) {
// 	if (err) {
// 		console.log(err);
// 	}
// 	else {
// 		DataBase.request (data).then ((response) => {
// 			console.log (response);
// 		});	
// 	}
// });


