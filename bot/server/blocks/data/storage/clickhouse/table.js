const _Table = require ('../structure/table.js');

const _CTable = _Table.extend ((scope) => {
	this.deploy = function () {
		return (
			'CREATE TABLE IF NOT EXISTS '+scope.name +
			'('+scope.format.fields.map ((field)=>{
				return field.name + field.type;
			}).join (', ')+')' +
			' ENGINE = MergeTree ('+scope.date_field+', ('+scope.key_fields+'), 8192)'
		)
	}
});

module.exports = _CTable;


