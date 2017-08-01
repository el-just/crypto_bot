var _Structure = require ('./structure.js');

_Set = _Structure.extend((source) => {
	this.get = source.get;
	this.set = source.set;
});

module.exports = _Set;