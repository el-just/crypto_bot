const crypto = require('crypto');

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
            query = 'CREATE TABLE IF NOT EXISTS '+this.owner.name+'.'+name+' ('+fields+')'+' ENGINE = MergeTree ('+this.format.date_field+', ('+this.format.key_fields+'), 8192)';

        this.owner.request (query).then ((result)=>{
            console.log (result);
        });
    }

    this.insertRow = function () {
        // 'INSERT INTO '+this.owner.name+'.'+name+' VALUES ('++')'
    }

    this.insertList = function (list) {
        var
            self = this,
            currentTime = parseInt (new Date ().getTime () / 1000, 10);

            formated_data = list.reduce ((previousValue, currentValue, index, array) => {
                var text_row = Object.keys(currentValue).reduce ((previous_tr, row_key, rowKeyIndex, rowKeys)=>{
                    return previous_tr+currentValue[row_key];
                }, '');

                currentValue.imprint = crypto.createHmac('sha256', self.name).update(text_row).digest('hex');

                currentValue.modify_date = new Date ().setHours (0,0,0,0)/1000;
                currentValue.modify_time = currentTime;
                return previousValue + JSON.stringify(currentValue) + '\n';
            }, ''),

            query = 'INSERT INTO '+this.owner.name+'.'+name+' FORMAT JSONEachRow\n'+formated_data;

        this.owner.request (query).then ((result)=>{
            console.log (result);
        });
    }
}

module.exports = Table;