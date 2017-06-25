var
	autobahn = require('autobahn'),
	db = require ('./db.js')
	connection = new autobahn.Connection({
	  url: "wss://api.poloniex.com",
	  realm: "realm1"
	});
var
	tickerOrder = [
		'currencyPair',
		'last',
		'lowestAsk',
		'highestBid',
		'percentChange',
		'baseVolume',
		'quoteVolume',
		'isFrozen',
		'24hrHigh',
		'24hrLow'
	]

connection.onopen = function (session) {
	function tickerEvent (args,kwargs) {
		var
			shortName = args[0];
		
		db.update (JSON.stringify (args)+',', 'ticker/'+shortName);
	}
	session.subscribe('ticker', tickerEvent);

	// function marketEvent (args,kwargs) {
	// 	console.log(args);
	// }
	// Chatty
	// function trollboxEvent (args,kwargs) {
	// 	console.log(args);
	// }
	//session.subscribe('BTC_XMR', marketEvent);
	//session.subscribe('trollbox', trollboxEvent);
}

connection.onclose = function () {
  console.log("Websocket connection closed");
}
		       
connection.open();