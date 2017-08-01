function _Block () {

}

_Block.extend = function (pure_next_block) {
	var
		current_block = this,

		next_block = function () {
			var scope;
			arguments.unshift (scope);
			current_block.apply (this, arguments);
			pure_next_block.apply (this, arguments);
		}

	for (property in current_block) {
		if (current_block.hasOwnProperty(property)) {
			next_block[property] = current_block[property];
		}
	}

	return next_block;
}

module.exports = _Block;