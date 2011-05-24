function(doc){
    if(doc.TYPE == 'Part'){
        emit(doc._id,doc);
    }
}
