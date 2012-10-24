function(doc) {
    if(doc.TYPE == 'Monograph' && doc.visible === true){
        emit(doc.title.toUpperCase().trim().substring(0, 1), 1);
    }
}
