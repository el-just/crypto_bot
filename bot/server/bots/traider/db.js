var
   fs = require('fs');
function update (data, storage) {
   if (data.then) {
      data.then (function (data){
         fs.appendFile('./bots/traider/db/'+storage+".d", data, function(err) {
            if(err) {
               return console.log(err);
            }
         });
      });
   }
   else {
      fs.appendFile('./bots/traider/db/'+storage+".d", data, function(err) {
         if(err) {
            return console.log(err);
         }
      });
   }
}

function read (storage) {
   return new Promise (function (resolve, reject) {
      fs.readFile('./bots/traider/db/'+storage+'.d', 'utf8', function (err,data) {
         if (err) {
            console.log(err);
            reject (err);
         }

         resolve (JSON.parse (data));
      });
   }); 
}

module.exports.update = update;
module.exports.read = read;