var
	Average = {};

Average.simple = function (values) {
	var
		summary = 0.0;

	for (value of values) {
		summary += parseFloat(value);
	}

	return summary / values.length;
}

Average.weighted = function (values) {
	var
		idx,
		weighted_summary = 0.0;

	for (idx = 0; idx < values.legth; idx ++) {
		weighted_summary += (i+1) * values[idx];
	}

	return 2 / (values.length * (values.length + 1)) * weighted_summary
}


module.exports = Average;