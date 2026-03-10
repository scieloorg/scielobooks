ROUTES = [
    {"name": "general.set_language", "pattern": "/setlang/", "view": "scielobooks.views.set_language"},
    {"name": "general.attach", "pattern": "/attach/id/{sbid}/{filename}", "view": "scielobooks.views.attach"},
    {"name": "general.favicon", "pattern": "/favicon.ico", "view": "scielobooks.views.favicon"},
    {"name": "catalog.cover", "pattern": "/id/{sbid}/cover/cover.jpeg", "view": "scielobooks.catalog.views.cover"},
    {"name": "catalog.cover_thumbnail", "pattern": "/id/{sbid}/cover/cover_thumbnail.jpeg", "view": "scielobooks.catalog.views.cover"},
    {"name": "catalog.book_details", "pattern": "/id/{sbid}", "view": "scielobooks.catalog.views.book_details", "renderer": "scielobooks:catalog/templates/book_details.pt"},
    {"name": "catalog.chapter_details", "pattern": "/id/{sbid}/{chapter}", "view": "scielobooks.catalog.views.chapter_details", "renderer": "scielobooks:catalog/templates/chapter_details.pt"},
    {"name": "catalog.pdf_file", "pattern": "/id/{sbid}/pdf/{part}.pdf", "view": "scielobooks.catalog.views.pdf_file"},
    {"name": "catalog.epub_file", "pattern": "/id/{sbid}/epub/{part}.epub", "view": "scielobooks.catalog.views.epub_file"},
    {"name": "catalog.swf_file", "pattern": "/id/{sbid}/swf/{part}.swf", "view": "scielobooks.catalog.views.swf_file"},
    {"name": "evaluation.books_list", "pattern": "/evaluation/list", "view": "scielobooks.staff.views.panel", "renderer": "scielobooks:evaluation/templates/books_list.pt", "permission": "editors"},
    {"name": "evaluation.book_details", "pattern": "/evaluation/id/{sbid}", "view": "scielobooks.staff.views.book_details_evaluation", "renderer": "scielobooks:evaluation/templates/book_details.pt", "permission": "editors"},
    {"name": "staff.delete_book", "pattern": "/staff/book/id/{sbid}", "view": "scielobooks.staff.views.delete_book", "permission": "admin", "request_method": "DELETE"},
    {"name": "staff.book_details", "pattern": "/staff/book/id/{sbid}", "view": "scielobooks.staff.views.book_details", "renderer": "scielobooks:staff/templates/book_details.pt", "permission": "admin"},
    {"name": "staff.new_book", "pattern": "/staff/book/new", "view": "scielobooks.staff.views.new_book", "renderer": "scielobooks:templates/form.pt", "permission": "admin"},
    {"name": "staff.edit_book", "pattern": "/staff/book/id/{sbid}/edit", "view": "scielobooks.staff.views.edit_book", "renderer": "scielobooks:templates/form.pt", "permission": "admin"},
    {"name": "staff.parts_list", "pattern": "/staff/book/id/{sbid}/parts", "view": "scielobooks.staff.views.parts_list", "renderer": "scielobooks:staff/templates/parts_list.pt", "permission": "admin"},
    {"name": "staff.new_part", "pattern": "/staff/book/id/{sbid}/parts/new", "view": "scielobooks.staff.views.new_part", "renderer": "scielobooks:templates/form.pt", "permission": "admin"},
    {"name": "staff.edit_part", "pattern": "/staff/book/id/{sbid}/parts/{part_id}/edit", "view": "scielobooks.staff.views.new_part", "renderer": "scielobooks:templates/form.pt", "permission": "admin"},
    {"name": "staff.panel", "pattern": "/staff/panel", "view": "scielobooks.staff.views.panel", "renderer": "scielobooks:staff/templates/panel.pt", "permission": "admin"},
    {"name": "staff.new_publisher", "pattern": "/staff/publisher/new", "view": "scielobooks.staff.views.new_publisher", "renderer": "scielobooks:templates/form.pt", "permission": "admin"},
    {"name": "staff.edit_publisher", "pattern": "/staff/publisher/{slug}/edit", "view": "scielobooks.staff.views.new_publisher", "renderer": "scielobooks:templates/form.pt", "permission": "admin"},
    {"name": "staff.publishers_list", "pattern": "/staff/publisher/list", "view": "scielobooks.staff.views.publishers_list", "renderer": "scielobooks:staff/templates/publishers_list.pt", "permission": "admin"},
    {"name": "staff.delete_publisher", "pattern": "/staff/publisher/{slug}", "view": "scielobooks.staff.views.delete_publisher", "permission": "admin", "request_method": "DELETE"},
    {"name": "staff.new_meeting", "pattern": "/staff/meeting/new", "view": "scielobooks.staff.views.new_meeting", "renderer": "scielobooks:templates/form.pt", "permission": "admin"},
    {"name": "staff.edit_meeting", "pattern": "/staff/meeting/{id}/edit", "view": "scielobooks.staff.views.new_meeting", "renderer": "scielobooks:templates/form.pt", "permission": "admin"},
    {"name": "staff.meetings_list", "pattern": "/staff/meeting/list", "view": "scielobooks.staff.views.meetings_list", "renderer": "scielobooks:staff/templates/meetings_list.pt", "permission": "admin"},
    {"name": "staff.delete_meeting", "pattern": "/staff/meeting/{id}", "view": "scielobooks.staff.views.delete_meeting", "permission": "admin", "request_method": "DELETE"},
    {"name": "staff.evaluation_attachments", "pattern": "/staff/book/id/{sbid}/attachs/{filename}", "view": "scielobooks.staff.views.evaluation_attachments", "permission": "editors"},
    {"name": "staff.ajax.set_meeting", "pattern": "/staff/function/setmeeting/", "view": "scielobooks.staff.views.ajax_set_meeting", "xhr": True, "permission": "admin"},
    {"name": "staff.ajax_set_committee_decision", "pattern": "/staff/function/setcommitteedecision/", "view": "scielobooks.staff.views.ajax_set_committee_decision", "xhr": True, "permission": "admin"},
    {"name": "staff.ajax_action_publish", "pattern": "/staff/function/actionpublish/", "view": "scielobooks.staff.views.ajax_action_publish", "xhr": True, "permission": "admin"},
    {"name": "staff.ajax_action_unpublish", "pattern": "/staff/function/actionunpublish/", "view": "scielobooks.staff.views.ajax_action_unpublish", "xhr": True, "permission": "admin"},
    {"name": "staff.ajax_action_delete_part", "pattern": "/staff/function/actiondeletepart/", "view": "scielobooks.staff.views.ajax_action_delete_part", "xhr": True, "permission": "admin"},
    {"name": "users.signup", "pattern": "/users/signup", "view": "scielobooks.users.views.signup", "renderer": "scielobooks:users/templates/signup_form.pt", "permission": "admin"},
    {"name": "users.login", "pattern": "/login", "view": "scielobooks.users.views.login", "renderer": "scielobooks:templates/form.pt"},
    {"name": "users.logout", "pattern": "/logout", "view": "scielobooks.users.views.logout"},
    {"name": "users.activation", "pattern": "/users/activation", "view": "scielobooks.users.views.activation", "renderer": "scielobooks:users/templates/activation.pt"},
    {"name": "users.forgot_password", "pattern": "/users/forgot_password", "view": "scielobooks.users.views.forgot_password", "renderer": "scielobooks:templates/form.pt"},
    {"name": "users.recover_password", "pattern": "/users/recover_password", "view": "scielobooks.users.views.recover_password", "renderer": "scielobooks:templates/form.pt"},
    {"name": "users.list", "pattern": "/users/list", "view": "scielobooks.users.views.users_list", "renderer": "scielobooks:users/templates/users_list.pt", "permission": "admin"},
    {"name": "users.edit_user", "pattern": "/users/id/{id}/edit", "view": "scielobooks.users.views.edit_user", "renderer": "scielobooks:users/templates/signup_form.pt", "permission": "admin"},
    {"name": "users.ajax.setactive", "pattern": "/users/function/setactive/", "view": "scielobooks.users.views.ajax_set_active", "xhr": True, "permission": "admin"},
    {"name": "users.ajax.setinactive", "pattern": "/users/function/setinactive/", "view": "scielobooks.users.views.ajax_set_inactive", "xhr": True, "permission": "admin"},
    {"name": "api.v1.list_publishers", "pattern": "/api/v1/publishers/", "view": "scielobooks.api.views.list_publishers", "renderer": "json"},
    {"name": "api.v1.list_alphasum", "pattern": "/api/v1/alphasum/", "view": "scielobooks.api.views.list_alphasum", "renderer": "json"},
    {"name": "api.v1.list_books", "pattern": "/api/v1/books/", "view": "scielobooks.api.views.list_books", "renderer": "json"},
    {"name": "api.v1.list_changes", "pattern": "/api/v1/changes/", "view": "scielobooks.api.views.list_changes", "renderer": "json"},
    {"name": "api.v1.show_book", "pattern": "/api/v1/book/{id}/", "view": "scielobooks.api.views.show_book", "renderer": "json"},
]


def includeme(config):
    for route in ROUTES:
        config.add_route(route["name"], route["pattern"])
        view_kwargs = {
            "route_name": route["name"],
            "view": route["view"],
        }
        for key in ("renderer", "permission", "request_method", "xhr"):
            if key in route:
                view_kwargs[key] = route[key]
        config.add_view(**view_kwargs)
