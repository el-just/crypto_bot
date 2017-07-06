const Socket = require('./socket.js');

function DataBase () {
	var _socket = new Socket ();

	this.request = function (request) {
		return new Promise ((resolve, reject) => {
			_socket.send (request).then ((response) => {
				resolve (response);
			});
		});
	}
}

module.exports = new DataBase ();