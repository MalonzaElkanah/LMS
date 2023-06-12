from library.users.urls import user_urls
from library.members.urls import member_urls
from library.books.urls import book_urls
from library.transactions.urls import transaction_urls

from library.views import IndexView


def app_urls(app):
    app.add_url_rule("/", view_func=IndexView.as_view("index"))

    user_urls(app)
    member_urls(app)
    book_urls(app)
    transaction_urls(app)
