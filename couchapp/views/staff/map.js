function(doc) {
    if (doc.TYPE == 'Monograph') {
        emit(doc._id, {'publisher':doc.publisher.toUpperCase().trim(),
                       'title':doc.title,
                             'monograph':doc.monograph,
                             'status':doc.status,
                             'meeting':doc.meeting,
                        'creators':doc.creators});
    }
}