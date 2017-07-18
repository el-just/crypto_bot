function _Source (source) {
	this.resolve = function () {
		if (source instanceof Promise) {
			return source;
		}
		else if (typeof source === 'function') {
			return new Promise ((resolve, reject)=>{
				resolve (source ());
			});
		}
		else {
			return new Promise ((resolve, reject)=>{
				resolve (source);
			});
		}
	}
}

module.exports = _Source;