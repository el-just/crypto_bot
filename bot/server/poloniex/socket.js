var
    autobahn = require ('autobahn'),
    connection = new autobahn.Connection({
      url: "wss://api.poloniex.com",
      realm: "realm1"
    });

connection.onopen = function (session) {
    function tickerEvent (args,kwargs) {
        console.log (JSON.stringify (args));
    }
    session.subscribe('ticker', tickerEvent);

    // function marketEvent (args,kwargs) {
    //     console.log(args);
    // }
    // Chatty
    // function trollboxEvent (args,kwargs) {
    //     console.log(args);
    // }
    //session.subscribe('BTC_XMR', marketEvent);
    //session.subscribe('trollbox', trollboxEvent);
}

connection.onclose = function () {
  console.log("Websocket connection closed");
}
               
connection.open();
console.log ('opened')
