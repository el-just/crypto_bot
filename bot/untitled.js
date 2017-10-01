function _Block () {
	console.log (1)
}

_Block.extend = function (pure_next_block) {
	var
		current_block = this,

		next_block = function () {
			current_block.apply (this, this.arguments);
			pure_next_block.apply (this, this.arguments);
		}

	for (property in current_block) {
		if (current_block.hasOwnProperty(property)) {
			next_block[property] = current_block[property];
		}
	}

	return next_block;
}

_Data = _Block.extend((a, b) => {
	console.log (2)
});

_B = _Data.extend (() => {console.log (3)})

new _Data ();
console.log ('================')
new _B ()

/*
Enum8('hello' = 1, 'world' = 2)
*/