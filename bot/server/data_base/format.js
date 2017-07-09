function Format (config) {
    var
        structure = config;
    this.getFieldType = function (field_name) {
        var field_idx = structure.names.findIndex ((name, idx)=>{
            return name === field_name;
        });
        return structure.types[field_idx];
    }

    this.getFields = function () {
        return structure.names;
    }
}

module.exports = Format;