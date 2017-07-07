function Table (name, format) {
    this.name = name;
    this.format = format;

    this.create = function () {
        var
            self = this,
            fields = this.format.names.reduce ((previousValue, currentValue, index, array) => {
                var commonPart = currentValue + ' ' + self.format.types[index];

                if (index === 0) {
                    return commonPart + ','
                }
                else if (index === array.length - 1) {
                    return previousValue + ' ' + commonPart;
                }
                else {
                    return previousValue + ' ' + commonPart + ', ';
                }
            }, ''),
            query = 'CREATE TABLE IF NOT EXISTS '+this.owner.name+'.'+name+' ('+fields+')';

        this.owner.request (query);
    }

    this.insert = function () {
        // 'INSERT INTO '+this.owner.name+'.'+name+' VALUES ('++')'
    }
}

module.exports = Table;