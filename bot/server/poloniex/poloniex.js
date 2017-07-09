const PoloniexSocket = require('./socket.js');
const DataBase = require('../data_base/data_base.js');

function Poloniex () {
    var
        _socket = new PoloniexSocket ();

    this.updateCurrencies = function () {
        _socket.returnCurrencies().then ((currencies) => {
        	currencies = DataBase.currencies.excludeExisted (currencies).then ((excluded_currencies)=>{
        		if (excluded_currencies && excluded_currencies.length > 0) {
        			DataBase.currencies.insertList (excluded_currencies);
        		}
        	});
        });
    }
}

module.exports = new Poloniex ();