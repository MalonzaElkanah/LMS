from flask.views import View
from flask import (
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
)
from marshmallow import ValidationError
from sqlalchemy import union_all

from library.models import db, Book, Member, Transaction
from library.utils import login_required
from library.books.schemas import CreateBookSchema, UpdateBookSchema

import uuid


class CreateBookView(View):
    methods = ["GET", "POST"]
    decorators = [
        login_required,
    ]

    _title = "Create Book"
    _form = {
        "isbn": "text",
        "name": "text",
        "author": "text",
        "edition": "text",
        "publisher": "text",
        "quantity": "number",
        "description": "textarea",
    }

    def dispatch_request(self):
        if request.method == "GET":
            return render_template(
                "forms.html", title=self._title, form=self._form, item={}
            )

        elif request.method == "POST":
            try:
                results = CreateBookSchema().load(request.form)
            except ValidationError as error:
                print(error)
                for key, value in error.messages.items():
                    flash(f"{key}: {value[0]}")
                    break

                return render_template(
                    "forms.html", title=self._title, form=self._form, item=request.form
                )

            book = Book(**results, added_by=g.user.uuid, uuid=str(uuid.uuid1()))

            db.session.add(book)
            db.session.commit()

            if book:
                return render_template(
                    "info.html",
                    title=f"{self._title} Success!",
                    message=f"""
                    Book Created. Click this
                    <a href="{url_for('books_retrieve', id=str(book.uuid))}">
                    link to view the new Book</a>.
                    """,
                )
            else:
                return render_template(
                    "info.html",
                    title=self._title,
                    message="Error Creating Book. Please try again later.",
                )


class ListBookView(View):
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

            if field == "isbn":
                stmt = db.select(Book).where(Book.isbn.contains(search))
            elif field == "author":
                stmt = db.select(Book).where(Book.author.contains(search))
            else:
                stmt = db.select(Book).where(Book.name.contains(search))

            books = db.session.execute(stmt).scalars()
        else:
            title = "All Books"
            books = Book.query.all()

        return render_template("books/book_list.html", title=title, items=books)


class RetrieveBookView(View):
    methods = [
        "GET",
    ]
    decorators = [
        login_required,
    ]

    def _get_item(self, uuid):
        book = Book.query.filter_by(uuid=str(uuid)).one_or_none()

        if book is None:
            return render_template(
                "info.html", title="Error 404", message="Error Book Not Found."
            )

        return book

    def dispatch_request(self, id):
        book = self._get_item(id)

        return render_template(
            "books/book_detail.html", title=f"'{book.name}' Details", item=book
        )


class UpdateBookView(View):
    methods = ["GET", "POST"]
    decorators = [
        login_required,
    ]

    _title = "Update Book"
    _form = {
        "isbn": "text",
        "name": "text",
        "author": "text",
        "edition": "text",
        "publisher": "text",
        "quantity": "number",
        "description": "textarea",
        "uuid": "hidden",
    }

    def _get_item(self, uuid):
        book = Book.query.filter_by(uuid=str(uuid)).one_or_none()

        if book is None:
            return render_template(
                "info.html", title="Error 404", message="Error Book Not Found."
            )

        return book

    def dispatch_request(self, id):
        book = self._get_item(id)

        if request.method == "GET":
            return render_template(
                "forms.html", title=self._title, form=self._form, item=book
            )

        elif request.method == "POST":
            try:
                results = UpdateBookSchema().load(request.form)

                if results["uuid"] != str(book.uuid):
                    raise ValidationError(
                        "Internal Server Error, Refresh the page and try again."
                    )

            except ValidationError as error:
                for key, value in error.messages.items():
                    flash(f"{key}: {value[0]}")
                    break

                return render_template(
                    "forms.html", title=self._title, form=self._form, item=request.form
                )

            book.isbn = results["isbn"]
            book.name = results["name"]
            book.author = results["author"]
            book.edition = results["edition"]
            book.quantity = results["quantity"]
            book.publisher = results["publisher"]
            book.description = results["description"]

            db.session.commit()

            flash("Book Updated!")

            return redirect(url_for("books_retrieve", id=str(book.uuid)))


class DeleteBookView(View):
    methods = [
        "GET",
    ]
    decorators = [
        login_required,
    ]

    def _get_item(self, uuid):
        book = Book.query.filter_by(uuid=str(uuid)).one_or_none()

        if book is None:
            return render_template(
                "info.html", title="Error 404", message="Error Book Not Found."
            )

        return book

    def dispatch_request(self, id):
        book = self._get_item(id)
        db.session.delete(book)
        db.session.commit()

        flash("Book Delete!")

        return redirect(url_for("books_list"))


class IssueBookView(View):
    methods = ["GET", "POST"]
    decorators = [
        login_required,
    ]

    def _get_item(self, uuid):
        book = Book.query.filter_by(uuid=str(uuid)).one_or_none()

        if book is None:
            return render_template(
                "info.html", title="Error 404", message="Error Book Not Found."
            )

        return book

    def dispatch_request(self, id):
        book = self._get_item(id)

        if book.status != "AVAILABLE":
            flash(f"Error: '{book.name}' is not Available for Issue!")

            return redirect(url_for("books_retrieve", id=str(book.uuid)))

        if request.method == "GET":

            args = dict(request.args)

            if args.get("search", None) is not None:
                search = request.args["search"]
                field = request.args.get("field", "title")

                title = f"Search results for {field}: '{search}'."

                if field == "id_number":
                    stmt = db.select(Member).where(Member.id_number.contains(search))
                else:
                    names = search.strip().split(" ")
                    if len(names) > 1:
                        stmt = (
                            db.select(Member)
                            .where(Member.first_name.contains(names[0]))
                            .where(Member.second_name.contains(names[1]))
                        )
                    else:
                        union = union_all(
                            db.select(Member).where(Member.first_name.contains(search)),
                            db.select(Member).where(
                                Member.second_name.contains(search)
                            ),
                        )
                        stmt = db.select(Member).from_statement(union)

                members = db.session.execute(stmt).scalars()
            else:
                title = "All Members"
                members = Member.query.all()

            return render_template("books/book_issue.html", title=title, items=members)
        elif request.method == "POST":
            # Get Member to be issued
            member_id = request.form.get("member")
            member = Member.query.filter_by(uuid=member_id).one_or_none()

            if member is None:
                return render_template(
                    "info.html", title="Error 404", message="Error Member Not Found."
                )

            if member.outstanding_fee >= current_app.config["OUTSTANDING_DEBT"]:
                flash(
                    f"Error: {member.first_name} has an outstanding "
                    f"debt of KES {member.outstanding_debt}!"
                )
                return redirect(url_for("books_issue", id=str(book.uuid)))

            transaction = Transaction(
                book=str(book.uuid),
                member=str(member.uuid),
                rate_per_day=current_app.config["RATE_PER_DAY"],
                rented_by=g.user.uuid,
                uuid=str(uuid.uuid1()),
            )

            db.session.add(transaction)
            db.session.commit()

            flash(f"'{book.name}' Issued!")

            return redirect(url_for("books_retrieve", id=str(book.uuid)))
