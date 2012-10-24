function(doc) {
    if(doc.TYPE == 'Monograph' && doc.visible === true){
        emit(doc.title.toUpperCase().substring(0, 1), 1);
    }
}
