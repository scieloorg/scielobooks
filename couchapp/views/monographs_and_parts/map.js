function(doc){
    if(doc.TYPE == 'Monograph'){
        emit([doc._id, 0], null);
    }
    if(doc.TYPE == 'Part'){
        emit([doc.monograph, 1], null);
    }
}