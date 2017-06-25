var
   db = require ('./db.js'),
   poloniex = require ('./poloniex.js'),
   ChartValue = require ('./ChartValue');

// db.update(poloniex.returnChartData({
//    currencyPair: 'BTC_GAME',
//    start:1489104000,
//    end:9999999999,
//    period:900
// }), 'chart/BTC_GAME');

//poloniex.buy();
//poloniex.sell();
BTC_balance = 0.5;
GAME_balance = 0;

raiseStarts = [];
currentRaise = undefined;
raisePower = undefined;

fallStarts = [];
fallPower = undefined;


var balance = 0;
db.read ('chart/BTC_GAME').then (function (chart){
   for (let i=1; i<chart.length; i++) {
      let
         currentFrame = chart[i],
         previousFrame = chart[i-1],

         currentValue = new ChartValue (currentFrame.close),
         previousValue = new ChartValue (previousFrame.close);

      if  (currentValue.exp !== previousValue.exp) {
         ChartValue.toPrecision (currentValue, previousValue);
      }

      if (currentValue.value > previousValue.value) {
         raiseStarts.push (currentFrame);
         console.log ('raise');
      }
      else if (currentValue.value < previousValue.value) {
         fallStarts.push (currentFrame);
         console.log ('fall');
      }
   }
});

// {
//    "date":1491782400,
//    "high":0.00038219,
//    "low":0.00037292,
//    "open":0.00038219,
//    "close":0.0003775,
//    "volume":4.89446814,
//    "quoteVolume":12977.67103631,
//    "weightedAverage":0.00037714
// }


// https://poloniex.com/public?command=returnChartData&currencyPair=BTC_XMR&start=1405699200&end=9999999999&period=14400
// 300, 900, 1800, 7200, 14400, and 86400