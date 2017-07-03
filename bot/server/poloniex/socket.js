var autobahn = require ('autobahn');

// function marketEvent (args,kwargs) {
//     console.log(args);
// }
// Chatty
// function trollboxEvent (args,kwargs) {
//     console.log(args);
// }
//session.subscribe('BTC_XMR', marketEvent);
//session.subscribe('trollbox', trollboxEvent);

function Socket () {
    var
        self = this,
        config = {
            poloniex_wss_url: 'wss://api.poloniex.com'
        },
        state = {
        };

    this.listen = function (ticker_event) {
        connection = new autobahn.Connection({
            url: config.poloniex_wss_url,
            realm: "realm1"
        });

        connection.onopen = function (session) {
            session.subscribe('ticker', ticker_event);
        }

        connection.onclose = function () {
            console.log("Websocket connection closed");
        }

        connection.open();
    }
}

module.exports = Socket;
