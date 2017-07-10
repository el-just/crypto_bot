const crypto = require ('crypto');
const Format = require ('./format.js');
const CSV = require ('./csv.js');

function Table (name, format) {
    this.name = name;
    this.format = format;

    function getHash (row) {
        var
            text_row = Object.keys(row).reduce ((previous_tr, row_key, rowKeyIndex, rowKeys)=>{
                return previous_tr+row[row_key];
            }, '');

        return crypto.createHmac('sha256', name).update(text_row).digest('hex');
    }

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
            currentDate = new Date ();

            list.forEach ((row, index, array) => {
                row.imprint = getHash (row);
                row.modify_date = currentDate;
                row.modify_time = currentDate;
            }),

            query = 'INSERT INTO '+this.owner.name+'.'+name+' FORMAT CSV\n'+self.toCSV(list);

        this.owner.request (query).then ((result)=>{
            console.log (result);
        });
    },

    this.excludeExisted = function (list) {
        var
            self = this,
            imprints = list.reduce ((query_text, row, idx)=>{
                var
                    common_query = query_text + '\'' + getHash (row) + '\'';
                return idx < list.length - 1 ? common_query + ', ' : common_query; 
            }, ''),
            query = 'SELECT groupArray(name) FROM (SELECT DISTINCT name, imprint FROM ej.currencies ORDER BY modify_date ASC) WHERE imprint IN ('+imprints+')'+' FORMAT CSV';

        return new Promise ((resolve, reject) => {
            self.owner.request (query).then ((result)=>{
                if (result.length > 0) {
                    console.log (result);
                    result = result.replace (/["\[\]\']/g,'').split(',');
                    resolve (list.reduce((excluded_list, row, idx) => {
                        if (result.findIndex ((name)=>{return name === row.name}) === -1) {
                            excluded_list.push (row);
                        }

                        return excluded_list;
                    }, []));
                }
            });
        });
    }

    this.toCSV = function (list) {
        return CSV.stringify (new Format (this.format), list);
    };

}

module.exports = Table;