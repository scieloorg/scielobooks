function(head, req) {
  var ddoc = this;
  var Mustache = require("lib/mustache");
  var row;
  var rows = [];

  while (row = getRow()) {
    row.value.kv_creators = [];
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
    // translated_title as key-value
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

  var html = Mustache.to_html(ddoc.templates.parts, context);
  return(html);
}
