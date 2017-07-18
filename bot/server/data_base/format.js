function Format (config) {
    var
        structure = config,
        extensions = {},
        data_sources = {};

    this.getFieldType = function (field_name) {
        var field_idx = structure.names.findIndex ((name, idx)=>{
            return name === field_name;
        });
        return structure.types[field_idx];
    }

    this.getFields = function () {
        return structure.names;
    }

    this.specifyEnum = function (field_name, values) {
        extensions[field_name] = values;
    }

    this.setEnumSource = function (name, source) {
        data_sources[name] = source;
    }
}

module.exports = Format;