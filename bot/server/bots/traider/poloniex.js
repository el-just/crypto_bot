// var Currency = {
//    id: undefined,
//    shortName: undefined,
//    fullName: undefined,
//    txFee: undefined,
//    minConf: undefined,
//    depositAddress: undefined,
//    disabled: undefined,
//    frozen: undefined
// }

var
   https = require ('https');

function sendPublicCommand (command, args) {
   return new Promise (function (resolve, reject) {
      var
         argsNames,
         reqOptions = {
            host: 'poloniex.com',
            path: '/public?command='+command
         };

      if (args) {
         argsNames = Object.keys(args);
         for (name of argsNames) {
            reqOptions.path += '&'+name+'='+args[name];
         }
      }

      https.get (reqOptions, function (res) {
         var
            bodyChunks = [];

         res.on('data', function(chunk) {
            bodyChunks.push(chunk);
         }).on('end', function() {
            var
               body = Buffer.concat(bodyChunks);

            resolve (body);
         });
      });
   });
}

function returnCurrencies () {
   return sendPublicCommand ('returnCurrencies')
}

function returnOrderBook () {
   return sendPublicCommand ('returnOrderBook', {currencyPair: 'all', depth:10})
}

function returnTicker () {
   return sendPublicCommand ('returnTicker')
}

function returnChartData (params) {
   return sendPublicCommand ('returnChartData', params)
}

function buy () {console.log('buy');}
function sell () {console.log('sell');}

module.exports.returnCurrencies = returnCurrencies;
module.exports.returnOrderBook = returnOrderBook;
module.exports.returnTicker = returnTicker;
module.exports.returnChartData = returnChartData;
module.exports.buy = buy;
module.exports.sell = sell;