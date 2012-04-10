function(doc, req) {
    var ddoc = this;
    var Mustache = require("lib/mustache");

    var individual_authors = [];
    var corporate_authors = [];
    var translators = [];
    var coordinators = [];
    var editors = [];
    var others = [];
    var organizers = [];
    var collaborators = [];
    var format = [];

    // creators
    for each(var value in doc.creators){
        var supposed_name = '';
        var current_role = '';
        // var is_author = false;
        for each(var item in value){
            if(item[0] == 'full_name'){
                supposed_name = item[1];
            }
            if(item[0] == 'role'){
                current_role = item[1];
            }
            if(supposed_name.length > 0 && current_role.length > 0){
                if(current_role == 'individual_author'){
                    individual_authors.push(supposed_name);
                    break;    
                } 
                else if(current_role == 'corporate_author'){
                    corporate_authors.push(supposed_name);
                    break;
                }
                else if(current_role == 'translator'){
                    translators.push(supposed_name);
                    break;
                }
                else if(current_role == 'coordinator'){
                    coordinators.push(supposed_name);
                    break;
                }
                else if(current_role == 'editor'){
                    editors.push(supposed_name);
                    break;
                } 
                else if(current_role == 'other'){
                    others.push(supposed_name);
                    break;
                }
                else if(current_role == 'organizer'){
                    organizers.push(supposed_name);
                    break;
                }
                else if(current_role == 'collaborator'){
                    collaborators.push(supposed_name);
                    break;
                }
                else{
                    break;
                }                            
            }
        }
    }
    
    var formatted_individual_authors = individual_authors.join('; ');
    var formatted_corporate_authors = corporate_authors.join('; ');
    var formatted_translators = translators.join('; ');
    var formatted_coordinators = coordinators.join('; ');
    var formatted_editors = editors.join('; ');
    var formatted_others = others.join('; ');
    var formatted_organizers = organizers.join('; ');
    var formatted_collaborators = collaborators.join('; ');

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
                authors: formatted_individual_authors,
                corporate_authors: formatted_corporate_authors,
                translators: formatted_translators,
                coordinators: formatted_coordinators,
                editors: formatted_editors,
                others: formatted_others,
                organizers: formatted_organizers,
                collaborators: formatted_collaborators,
                format: formatted_format,
                shortname: doc.shortname,
                language: doc.language,
                publication_date: doc.publication_date,

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
        result.year = doc.monograph_year;
        var html = Mustache.to_html(ddoc.templates.solr_feed_showpart, result);
    }
    else{
        result.type = 'book';
        result.synopsis = doc.synopsis;
        result.title = doc.title;
        result.isbn = doc.isbn;
        result.publisher = doc.publisher;
        result.year = doc.year;
        var html = Mustache.to_html(ddoc.templates.solr_feed_showbook, result);
    }

    return(html);
}
