function CSV () {
    function toDate (value) {
        if (value instanceof Date) {
            return '\'' + value.toISOString().split('T')[0] + '\'';
        }
    }

    function toDateTime (value) {
        if (value instanceof Date) {
            return '\'' + value.toISOString().split('.')[0].replace('T', ' ') + '\'';
        }
    }

    function toString (value) {
        return '\''+(value?value.replace('\'', '\'\''):'NULL')+'\''
    }

    function toInt (value) {
        return parseInt (value, 10) + '';
    }

    function toFloat (value) {
        return parseFloat (value, 10)+'';
    }

    var transforms = {
        'Date': toDate,
        'DateTime': toDateTime,
        'String': toString,
        'UInt32': toInt,
        'Float64': toFloat,
        'UInt8': toInt
    }

    this.stringify = function (format, data_set) {
        return data_set.reduce ((formated_data, row, index) => {
            var
                common_text_row = format.getFields().reduce((text_row, field, field_idx) => {
                    var
                        common_text_row_part = text_row + transforms[format.getFieldType (field)] (row[field]);
                    
                    return field_idx < Object.keys(row).length - 1 ? common_text_row_part + ', ' : common_text_row_part;
                }, '');

            return index < data_set.length - 1 ? formated_data + common_text_row +  '\n' : formated_data + common_text_row;
        }, '');
    }
}

module.exports = new CSV ();