// const s = require ('./poloniex/poloniex.js');
// s.getBitterxC().then ((result)=>{console.log (result)})


const http = require('http');
const Router = require('./router.js');
const WebSocketServer = require('./sockets/web_browser.js');

const hostname = '0.0.0.0';
const port = 3000;

var
  router = new Router ();

const server = http.createServer((req, res) => {
  console.log ('Request accepted');
  router.resolveAction (req).then ((actionResult) => {
    router.responseClient(req, res, actionResult);
  });
});

server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});