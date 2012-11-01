function(doc){
    if(doc.TYPE == 'Part'){
        if(doc.visible == true)
        emit(doc._id, doc);
    }
}
