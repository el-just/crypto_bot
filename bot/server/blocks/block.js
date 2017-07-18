function _Block () {

}

_Block.prototype.extend = function (next_block) {
	next_block.prototype = Object.create(_Block.prototype);
	next_block.prototype.constructor = next_block;
}

module.exports = _Block;