function(doc, req) {
    var ddoc = this;
    var Mustache = require("lib/mustache");

    var authors = [];
    var format = [];

    // creators
    for each(var value in doc.creators){
        var supposed_name = '';
        var is_author = false;
        for each(var item in value){
            if(item[0] == 'full_name'){
                supposed_name = item[1];
            }
            if(item[0] == 'role' && item[1].search('author$') >= 0){
                is_author = true;
            }
            if(supposed_name.length > 0 && is_author == true){
                authors.push(supposed_name);
                break;
            }
        }
    }
    var formatted_creators = authors.join('; ');

    // format
    var supposed_height = null;
    var supposed_width = null;
    var formatted_format = '';
    for each(var value in doc.format){
        if(value[0] == 'height' && value[1] !== null){
            supposed_height = value[1];
        }
        if(value[0] == 'width' && value[1] !== null){
            supposed_width = value[1];
        }
    }
    if(supposed_height !== null && supposed_width !== null){
        format.push(supposed_height);
        format.push(supposed_width);
        formatted_format = format.join(' x ');
    }

    // common data
    var result = {
                sbid: doc._id,
                authors: formatted_creators,
                format: formatted_format,
                shortname: doc.shortname,
                language: doc.language,
                year: doc.year,
                }

    // visibility flag
    if (doc.visible==true){
        result['is_public'] = true;
    } else {
        result['is_public'] = false;
    }

    // type specific data
    if(doc.TYPE == 'Part'){
        result.type = "part";
        result.book_title = doc.monograph_title;
        result.isbn = doc.monograph_isbn;
        result.title = doc.title;
        result.chapterorder = doc.order;
        result.monographsbid = doc.monograph;
        result.publisher = doc.monograph_publisher;
        var html = Mustache.to_html(ddoc.templates.solr_feed_showpart, result);
    }
    else{
        result.type = 'book';
        result.synopsis = doc.synopsis;
        result.title = doc.title;
        result.isbn = doc.isbn;
        result.publisher = doc.publisher;
        var html = Mustache.to_html(ddoc.templates.solr_feed_showbook, result);
    }

    return(html);
}
