function(head, req) {
    var ddoc = this;
    var Mustache = require("lib/mustache");
    var head_list = [];
    var rows = [];
    var row;

    start({
        "headers":{
            "Content-Type": "text/html; charset=utf-8"
        }
    });

    for(k in head){
        head_list.push({'key':k,'value':head[k]});
    }

    while(row = getRow()) {
        var authors = [];
        var format = [];        
        
        for each (var value in row.value.creator)
            authors.push({'name':value});
        for each(var value in row.value.format)
            format.push({'type':value});            

        rows.push({
                   sbid: row.value._id,
                   authors: authors,
                   format: format,
                   shortname: row.value.shortname,
                   title: row.value.title,
                   isbn: row.value.isbn,
                   type: 'book',
                   publisher: row.value.publisher,
                   language: row.value.language,
                   year: row.value.year,
                   synopsis: row.value.synopsis,
                   });
    }
    
    var view = {
        head: head_list,
        rows: rows,
    }
    
    var html = Mustache.to_html(ddoc.templates.solr_feed_books, view);
    return(html);               
};
