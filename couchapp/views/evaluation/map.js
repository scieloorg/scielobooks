function(doc) {
    if (doc.TYPE == 'Evaluation') {
        emit(doc.publisher.toUpperCase().trim(), {'title':doc.title,
                             'monograph':doc.monograph,
                             'status':doc.status});
    }
}