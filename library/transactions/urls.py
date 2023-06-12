from library.transactions.views import (
    ListTransactionView,
    RetrieveTransactionView,
    DeleteTransactionView,
    BookReturnView,
    PayOutstandingFeeView,
)


def transaction_urls(app):
    app.add_url_rule(
        "/transactions/", view_func=ListTransactionView.as_view("transactions_list")
    )
    app.add_url_rule(
        "/transactions/<uuid:id>/",
        view_func=RetrieveTransactionView.as_view("transactions_retrieve"),
    )
    app.add_url_rule(
        "/transactions/<uuid:id>/delete/",
        view_func=DeleteTransactionView.as_view("transactions_delete"),
    )
    app.add_url_rule(
        "/transactions/<uuid:id>/return-book/",
        view_func=BookReturnView.as_view("transactions_return-book"),
    )
    app.add_url_rule(
        "/transactions/<uuid:id>/pay-fee/",
        view_func=PayOutstandingFeeView.as_view("transactions_pay-fee"),
    )
