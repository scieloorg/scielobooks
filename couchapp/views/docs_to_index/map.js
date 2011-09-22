function(doc) {
    if (doc.TYPE == 'Monograph' || doc.TYPE == 'Part') {
        if (doc.visible == true) {
            emit(doc._id, null);       
        }
    }
}