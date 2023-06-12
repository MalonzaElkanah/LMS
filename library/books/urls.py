from library.books.views import (
    CreateBookView,
    ListBookView,
    RetrieveBookView,
    UpdateBookView,
    DeleteBookView,
    IssueBookView,
)


def book_urls(app):
    app.add_url_rule("/books/", view_func=ListBookView.as_view("books_list"))
    app.add_url_rule("/books/create/", view_func=CreateBookView.as_view("books_create"))
    app.add_url_rule(
        "/books/<uuid:id>/", view_func=RetrieveBookView.as_view("books_retrieve")
    )
    app.add_url_rule(
        "/books/<uuid:id>/update/", view_func=UpdateBookView.as_view("books_update")
    )
    app.add_url_rule(
        "/books/<uuid:id>/delete/", view_func=DeleteBookView.as_view("books_delete")
    )
    app.add_url_rule(
        "/books/<uuid:id>/issue/", view_func=IssueBookView.as_view("books_issue")
    )
