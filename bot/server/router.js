var fileSystem = require ('./sockets/file_system.js');

function Router () {
  var self = this;

  this.resolveAction = function (req) {
    return new Promise (function (resolve, reject) {
      if (req.method === 'GET') {
        self.getFile (req.url && req.url !== '/' ? '../client'+req.url : "../client/index.html").then (file => {
          resolve (file);
        });
      }
      else {
        self.getData ().then(data => {
          resolve (data)
        });
      }
    });
  }

  this.getFile = function (path) {
    return new Promise ((resolve, reject) => {
      fileSystem.File.get (path, (err, fileData) => {
        if (err) {
          console.log (err);
          resolve (false);
        }
        else {
          resolve ({
            extension: fileSystem.File.getExt (path),
            content: fileData
          });
        }
      });
    });
  }

  this.getData = function () {
    return new Promise ((resolve, reject) => {
      fileSystem.File.get ('bots/traider/db/chart/BTC_GAME.d', (err, fileData) => {
        if (err) {
          console.log (err);
          resolve (false);
        }
        else {
          resolve (fileData);
        }
      });
    });
  }

  this.responseClient = function (req, res, actionResult) {
    if (req.method === 'GET') {
      if (actionResult) {
        res.setHeader("Content-Type", fileSystem.File.mimes[actionResult.extension]);
        res.statusCode = 200;
        res.end(actionResult.content);
      }
      else {
        res.writeHead(404);
        res.end();
      }
    }
    else {
      res.setHeader ("Content-Type", "application/json")
      
      if (actionResult) {
        res.statusCode = 200;
        res.end(actionResult);
      }
      else {
        res.statusCode = 500;
        res.end ();
      }
      
      // var data = '';
      // req.on('data', function(chunk) {
      //   data += chunk.toString();
      // });
      
    }
  }
}

module.exports = Router;