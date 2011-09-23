function(doc, req) {
    var ddoc = this;
    var Mustache = require("lib/mustache");

    var authors = [];
    var format = [];

    for each (var value in doc.creators){
        var supposed_name = '';
        var is_author = false;
        for each(var item in value){
            if(item[0] == '_'){
                supposed_name = item[1];
            }
            if(item[0] == 'role' && item[1] == 'author'){
                is_author = true;
            }
            if(supposed_name.length > 0 && is_author == true){
                authors.push({'name':supposed_name});
            }
        }
    }
    for each(var value in doc.format){
        format.push({'type':value});        
    }
    var result = {
                sbid: doc._id,
                monographsbid: doc.monograph,
                authors: authors,
                format: format,
                shortname: doc.shortname,
                isbn: doc.isbn,
                publisher: doc.publisher,
                language: doc.language,
                year: doc.year,
                chapterorder: doc.order
                }

    if(doc.TYPE == 'Part'){
        result.type = "part";
        result.book_title = doc.title;
        result.title = doc.chaptertitle;
        var html = Mustache.to_html(ddoc.templates.solr_feed_showpart, result);
    }
    else{
        var chapters_list = [];
        for each(var value in doc.chapterslist)
            chapters_list.push({'title':value.chaptertitle});
        result.chapters_list = chapters_list;
        result.type = 'book';
        result.synopsis = doc.synopsis;
        result.title = doc.title;
        var html = Mustache.to_html(ddoc.templates.solr_feed_showbook, result);
    }

    return(html);
}
