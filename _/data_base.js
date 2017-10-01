function DataBase () {
	this.insert = function (table_name, data) {
		return new Promise ((resolve, reject) => {
			resolve (data);
		});
	}
}

module.exports = DataBase;