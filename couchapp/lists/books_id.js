function(head, req) {
  var ddoc = this;
  var Mustache = require("lib/mustache");
  var row;
  var rows = [];

  while (row = getRow()) {
    row.value.kv_creators = [];
    row.value.kv_shopping_info = [];
    row.value.kv_bisac_code = [];
    row.value.kv_format = [];
    row.value.kv_serie = [];
    row.value.kv_collection = [];
    row.value.kv_translated_titles = [];

    // creators as key-value
    for each (var creator in row.value.creators) {
      var fields = {};
      for each (var field in creator) {
        if (field === null) {
          continue;
        }
        fields[field[0]] = field[1];
      }
      row.value.kv_creators.push(fields);
    }
    // shopping info as key-value
    for each (var info in row.value.shopping_info) {
      var fields = {};
      for each (var field in info) {
        if (field === null) {
          continue;
        }
        fields[field[0]] = field[1];
      }
      row.value.kv_shopping_info.push(fields);
    }
    // bisac code as key-value
    for each (var bcode in row.value.bisac_code) {
      var fields = {};
      for each (var field in bcode) {
        if (field === null) {
          continue;
        }
        fields[field[0]] = field[1];
      }
      row.value.kv_bisac_code.push(fields);
    }
    // format as key-value
    for each (var format in row.value.format) {
      var fields = {};
      for each (var field in format) {
        if (field === null) {
          continue;
        }
        fields[field[0]] = field[1];
      }
      row.value.kv_format.push(fields);
    }
    // serie as key-value
    var serie_fields = {};
    for each (var field in row.value.serie) {
      if (field === null) {
        continue;
      }
      serie_fields["_"+field[0]] = field[1];
    }
    row.value.kv_serie.push(serie_fields);
    // collection as key-value
    var collection_fields = {};
    for each (var field in row.value.collection) {
      if (field === null) {
        continue;
      }
      collection_fields["_"+field[0]] = field[1];
    }
    row.value.kv_collection.push(collection_fields);
    // format as key-value
    for each (var t_title in row.value.translated_titles) {
      var fields = {};
      for each (var field in t_title) {
        if (field === null) {
          continue;
        }
        fields["_"+field[0]] = field[1];
      }
      row.value.kv_translated_titles.push(fields);
    }

    rows.push(row.value);
  }

  var context = {rows: rows};

  var html = Mustache.to_html(ddoc.templates.books, context);
  return(html);
}
