function(doc){
    if(doc.TYPE == 'Monograph'){
        if(doc.visible == true)
        emit(doc._id, doc);
    }
}
