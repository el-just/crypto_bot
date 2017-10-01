const resolve = function (event, data) {
	if (event.name === 'market.update') {
		
	}
}

module.exports = function (stock) {
	const
		self = this;

	stock.listen (() => {
		resolve.apply (self, arguments);
	});
}