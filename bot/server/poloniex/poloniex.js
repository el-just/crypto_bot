const PoloniexSocket = require('./socket.js');

function Poloniex () {
    var
        _socket = new PoloniexSocket ();

    this.updateCurrencies = function () {
        _socket.returnCurrencies().then ((currencies) => {
            
            console.log(currencies.length);
        });
    }
}

module.exports = new Poloniex ();