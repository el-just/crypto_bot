const _Type = require ('./type.js');
const _Set = require ('../structure/set.js');
const _Source = require ('../source.js');

const set_source = new _Source ();
const int_set = new _Set (set_source);

_Int = _Type.extend(() => {
	var
		value_set = int_set;
}

module.exports = _Int;