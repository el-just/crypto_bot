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

var
   https = require ('https');

https://bittrex.com/api/v1.1/public/getcurrencies

function Socket () {
    var
        self = this,
        // config = {
        //     poloniex_main_url: 'poloniex.com',
        //     poloniex_wss_url: 'wss://api.poloniex.com',
        //     poloniex_api_path: '/public'
        // },
        config = {
            poloniex_main_url: 'bittrex.com',
            poloniex_wss_url: 'wss://api.poloniex.com',
            poloniex_api_path: '/api/v1.1/public'
        },
        state = {
        };

    function _request (command, args) {
        return new Promise ((resolve, reject) => {
            var
                argsNames,
                reqOptions = {
                    host: config.poloniex_main_url,
                    // path: config.poloniex_api_path+'?command='+command
                    path: config.poloniex_api_path+'/'+command
                };

            if (args) {
                argsNames = Object.keys(args);
                for (name of argsNames) {
                    reqOptions.path += '&'+name+'='+args[name];
                }
            }

            https.get (reqOptions,  (res) => {
                var
                    bodyChunks = [];

                res.on('data', (chunk) => {
                    bodyChunks.push(chunk);
                }).on('end', () => {
                    var
                        body = Buffer.concat(bodyChunks);

                    resolve (JSON.parse(body.toString('utf8')));
                });
            });
        });
    }

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

    this.returnCurrencies = function () {
        return new Promise ((resolve, reject) => {
            _request ('returnCurrencies').then ((currencies_data) => {
                var currencies = [];
                Object.keys(currencies_data).forEach ((currency_name) => {
                    currencies.push ({
                        name: currency_name,
                        full_name: currencies_data[currency_name]['name'],
                        id: currencies_data[currency_name]['id'],
                        tax_fee: currencies_data[currency_name]['txFee'],
                        min_conf: currencies_data[currency_name]['minConf'],
                        deposit_address: currencies_data[currency_name]['depositAddress'],
                        is_disabled: currencies_data[currency_name]['disabled'],
                        is_delisted: currencies_data[currency_name]['delisted'],
                        is_frozen: currencies_data[currency_name]['frozen']
                    });
                });

                resolve (currencies);
            });
        });
    }

    this.returnBCurrencies = function () {
        return _request ('getcurrencies');
    }
}

module.exports = Socket;
