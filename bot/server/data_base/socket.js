var
   http = require ('http');

function Socket () {
    this.send = function (request) {
        return new Promise ((resolve, reject)=>{
            var
                post_options = {
                    host: 'localhost',
                    port: '8123',
                    path: '/',
                    method: 'POST',
                    headers: {
                        'Content-Length': Buffer.byteLength(request)
                    }
                },

                post_req = http.request(post_options, function(res) {
                    var
                        body_chunks = [];

                    res.on('data', (chunk) => {
                        body_chunks.push(chunk);
                    }).on('end', () => {
                        resolve (Buffer.concat(body_chunks).toString('utf8'));
                    });
                });

            post_req.write (request);
            post_req.end ();
        });
    }
}

module.exports = Socket;