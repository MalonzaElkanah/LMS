from flask.views import View
from flask import (
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import union_all

from library.models import db, Transaction, Member, Book
from library.utils import login_required

import datetime as dt


class ListTransactionView(View):
    methods = [
        "GET",
    ]
    decorators = [
        login_required,
    ]

    def dispatch_request(self):

        args = dict(request.args)

        if args.get("search", None) is not None:
            search = request.args["search"]
            field = request.args.get("field", "title")

            title = f"Search results for {field}: '{search}'."

            if field == "id":
                stmt = db.select(Transaction).where(Transaction.uuid.contains(search))
            elif field == "book":
                stmt = (
                    db.select(Transaction)
                    .join(Transaction.book_rent)
                    .where(Book.name.contains(search))
                )
            elif field == "member":
                names = search.strip().split(" ")
                if len(names) > 1:
                    stmt = (
                        db.select(Transaction)
                        .join(Transaction.member_rent)
                        .where(Member.first_name.contains(names[0]))
                        .where(Member.second_name.contains(names[1]))
                    )
                else:
                    union = union_all(
                        db.select(Transaction)
                        .join(Transaction.member_rent)
                        .where(Member.first_name.contains(search)),
                        db.select(Transaction)
                        .join(Transaction.member_rent)
                        .where(Member.second_name.contains(search)),
                    )
                    stmt = db.select(Transaction).from_statement(union)
            else:
                stmt = db.select(Transaction).where(Transaction.uuid.contains(search))

            transactions = db.session.execute(stmt).scalars()
        else:
            title = "All Transactions"
            transactions = Transaction.query.all()

        return render_template(
            "transactions/transaction_list.html", title=title, items=transactions
        )


class RetrieveTransactionView(View):
    methods = [
        "GET",
    ]
    decorators = [
        login_required,
    ]

    def _get_item(self, uuid):
        transaction = Transaction.query.filter_by(uuid=str(uuid)).one_or_none()

        if transaction is None:
            return render_template(
                "info.html", title="Error 404", message="Error Transaction Not Found."
            )

        return transaction

    def dispatch_request(self, id):
        transaction = self._get_item(id)

        return render_template(
            "transactions/transaction_detail.html",
            title=f"'{transaction.uuid}' Details",
            item=transaction,
        )


class DeleteTransactionView(View):
    methods = [
        "GET",
    ]
    decorators = [
        login_required,
    ]

    def _get_item(self, uuid):
        transaction = Transaction.query.filter_by(uuid=str(uuid)).one_or_none()

        if transaction is None:
            return render_template(
                "info.html", title="Error 404", message="Error Transaction Not Found."
            )

        return transaction

    def dispatch_request(self, id):
        transaction = self._get_item(id)
        db.session.delete(transaction)
        db.session.commit()

        flash("Transaction Delete!")

        return redirect(url_for("transactions_list"))


class BookReturnView(View):
    methods = ["GET", "POST"]
    decorators = [
        login_required,
    ]

    _title = "Book Return"
    _form = {
        "book": "disabled",
        "member": "disabled",
        "date_issued": "disabled",
        "date_returned": "disabled",
        "rent_fee": "disabled",
        "paid": "checkbox",
    }

    def _get_item(self, uuid):
        transaction = Transaction.query.filter_by(uuid=str(uuid)).one_or_none()

        if transaction is None:
            return render_template(
                "info.html", title="Error 404", message="Error Transaction Not Found."
            )

        return transaction

    def dispatch_request(self, id):
        transaction = self._get_item(id)

        if transaction.status not in ["RENTED", "OVERDUE"]:
            flash("Error, the book has already been returned.")

            return redirect(url_for("transactions_retrieve", id=str(transaction.uuid)))

        if request.method == "GET":
            data = {
                "book": transaction.book_rent.name,
                "member": f"{transaction.member_rent.name}",
                "date_issued": f"{transaction.rent_date: %d-%m-%y %H:%M:%S}",
                "date_returned": f"{dt.datetime.now().astimezone(): %d-%m-%y %H:%M:%S}",
                "rent_days": transaction.rent_days,
                "rent_fee": transaction.rent_fee,
                "status": transaction.status,
                "paid": False,
            }

            return render_template(
                "forms.html", title=self._title, form=self._form, item=data
            )

        elif request.method == "POST":
            if request.form.get("paid", False) == "on":
                transaction.rent_paid = True
                flash(
                    f"'{transaction.book_rent.name}' has been returned and "
                    "outstanding fee has bee paid!"
                )
            else:
                flash(
                    f"'{transaction.book_rent.name}' has been returned. "
                    "NOTE: Outstanding fee NOT PAID!"
                )

            transaction.returned_by = g.user.uuid
            transaction.return_date = dt.datetime.now().astimezone()

            db.session.commit()

            return redirect(url_for("transactions_retrieve", id=str(transaction.uuid)))


class PayOutstandingFeeView(View):
    methods = ["GET", "POST"]
    decorators = [
        login_required,
    ]

    def _get_item(self, uuid):
        transaction = Transaction.query.filter_by(uuid=str(uuid)).one_or_none()

        if transaction is None:
            return render_template(
                "info.html", title="Error 404", message="Error Transaction Not Found."
            )

        return transaction

    def dispatch_request(self, id):
        transaction = self._get_item(id)

        transaction.rent_paid = True
        db.session.commit()

        flash(f"'{transaction.book_rent.name}' outstanding fee has been PAID!")

        return redirect(url_for("transactions_retrieve", id=str(transaction.uuid)))
