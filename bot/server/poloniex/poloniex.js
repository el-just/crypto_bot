const PoloniexSocket = require('./socket.js');
const DataBase = require('../data_base/data_base.js');

function Poloniex () {
    var
        _socket = new PoloniexSocket ();

    this.updateCurrencies = function () {
        _socket.returnCurrencies().then ((currencies) => {
        	DataBase.currencies.insertList (currencies)
        });
    }
}

module.exports = new Poloniex ();