var
   http = require ('http');

function Socket () {
    var
        post_options = {
            host: 'localhost',
            port: '8123',
            path: '/',
            method: 'POST',
            headers: {
                'Content-Length': Buffer.byteLength(post_data)
            }
        },

        post_req = http.request(post_options, function(res) {
            var
                bodyChunks = [];

            res.on('data', (chunk) => {
                bodyChunks.push(chunk);
            }).on('end', () => {
                var
                    body = Buffer.concat(bodyChunks);

                resolve (body.toString('utf8'));
            });
        });

    post_req.write ('SELECT 1');
    post_req.end ();
}