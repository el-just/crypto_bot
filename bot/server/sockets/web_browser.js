var WebSocketServer = new require('ws');
var db = require ('../bots/traider/db.js');

// подключенные клиенты
var clients = {};

// WebSocket-сервер на порту 8081
var 
  webSocketServer = new WebSocketServer.Server({
      port: 8081
  });
webSocketServer.on('connection', function(ws) {

  var id = Math.random();
  console.log("новое соединение " + id);

  clients[id+''] = ws;

  ws.on('message', function(message) {
    console.log('получено сообщение ' + message);
  });

  ws.on('close', function() {
    console.log('соединение закрыто ' + id);
    delete clients[id+''];
  });
});

var itemId = 0;
db.read ('chart/BTC_GAME').then (function (chart){
  setInterval (()=>{
    for (let clientId of Object.keys(clients)) {
      if (itemId >= chart.legnth) {
        itemId = 0;
      }
      clients[clientId].send (JSON.stringify(chart[itemId]));
      itemId++;
    }
  }, 1000);
});