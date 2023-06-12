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

from library.models import db, Member, Book, Transaction
from library.utils import login_required
from library.members.schemas import CreateMemberSchema, UpdateMemberSchema

import uuid


class CreateMemberView(View):
    methods = ["GET", "POST"]
    decorators = [
        login_required,
    ]

    _title = "Create Member"
    _form = {"first_name": "text", "second_name": "text", "id_number": "text"}

    def dispatch_request(self):
        if request.method == "GET":
            return render_template(
                "forms.html", title=self._title, form=self._form, item={}
            )

        elif request.method == "POST":
            try:
                results = CreateMemberSchema().load(request.form)
            except ValidationError as error:
                print(error)
                for key, value in error.messages.items():
                    flash(f"{key}: {value[0]}")
                    break

                return render_template(
                    "forms.html", title=self._title, form=self._form, item=request.form
                )

            member = Member(**results, added_by=g.user.uuid, uuid=str(uuid.uuid1()))

            db.session.add(member)
            db.session.commit()

            if member:
                return render_template(
                    "info.html",
                    title=f"{self._title} Success!",
                    message=f"""
                    Member Created. Click this
                    <a href="{url_for('members_retrieve', id=str(member.uuid))}">
                    link to view the new Member</a>.
                    """,
                )
            else:
                return render_template(
                    "info.html",
                    title=self._title,
                    message="Error Creating member. Please try again later.",
                )


class ListMemberView(View):
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
                        db.select(Member).where(Member.second_name.contains(search)),
                    )
                    stmt = db.select(Member).from_statement(union)

            members = db.session.execute(stmt).scalars()
        else:
            title = "All Members"
            members = Member.query.all()

        return render_template("members/member_list.html", title=title, items=members)


class RetrieveMemberView(View):
    methods = [
        "GET",
    ]
    decorators = [
        login_required,
    ]

    def _get_item(self, uuid):
        member = Member.query.filter_by(uuid=str(uuid)).one_or_none()

        if member is None:
            return render_template(
                "info.html", title="Error 404", message="Error Member Not Found."
            )

        return member

    def dispatch_request(self, id):
        member = self._get_item(id)

        return render_template(
            "members/member_detail.html",
            title=f"{member.first_name} Details",
            item=member,
        )


class UpdateMemberView(View):
    methods = ["GET", "POST"]
    decorators = [
        login_required,
    ]

    _title = "Update Member"
    _form = {
        "first_name": "text",
        "second_name": "text",
        "id_number": "text",
        "uuid": "hidden",
    }

    def _get_item(self, uuid):
        member = Member.query.filter_by(uuid=str(uuid)).one_or_none()

        if member is None:
            return render_template(
                "info.html", title="Error 404", message="Error Member Not Found."
            )

        return member

    def dispatch_request(self, id):
        member = self._get_item(id)

        if request.method == "GET":
            return render_template(
                "forms.html", title=self._title, form=self._form, item=member
            )

        elif request.method == "POST":
            try:
                results = UpdateMemberSchema().load(request.form)

                if results["uuid"] != str(member.uuid):
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

            member.first_name = results["first_name"]
            member.second_name = results["second_name"]
            member.id_number = results.get("id_number")

            db.session.commit()

            flash("Member Updated!")

            return redirect(url_for("members_retrieve", id=str(member.uuid)))


class DeleteMemberView(View):
    methods = [
        "GET",
    ]
    decorators = [
        login_required,
    ]

    def _get_item(self, uuid):
        member = Member.query.filter_by(uuid=str(uuid)).one_or_none()

        if member is None:
            return render_template(
                "info.html", title="Error 404", message="Error Member Not Found."
            )

        return member

    def dispatch_request(self, id):
        member = self._get_item(id)
        db.session.delete(member)
        db.session.commit()

        flash("Member Delete!")

        return redirect(url_for("members_list"))


class IssueBookView(View):
    methods = ["GET", "POST"]
    decorators = [
        login_required,
    ]

    def _get_item(self, uuid):
        member = Member.query.filter_by(uuid=str(uuid)).one_or_none()

        if member is None:
            return render_template(
                "info.html", title="Error 404", message="Error Member Not Found."
            )

        return member

    def dispatch_request(self, id):
        member = self._get_item(id)

        if member.outstanding_fee >= current_app.config["OUTSTANDING_DEBT"]:
            flash(
                f"Error: {member.first_name} has an outstanding "
                f"debt of KES {member.outstanding_debt}!"
            )
            return redirect(url_for("member-books_issue", id=str(member.uuid)))

        if request.method == "GET":

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

            return render_template("members/book_issue.html", title=title, items=books)
        elif request.method == "POST":
            # Get Book to be issued
            book_id = request.form.get("book")
            book = Book.query.filter_by(uuid=book_id).one_or_none()

            if book is None:
                return render_template(
                    "info.html", title="Error 404", message="Error Book Not Found."
                )

            if book.status != "AVAILABLE":
                flash(f"Error: '{book.name}' is not Available for Issue!")

                return redirect(url_for("member-books_issue", id=str(member.uuid)))

            transaction = Transaction(
                book=str(book.uuid),
                member=str(member.uuid),
                rate_per_day=current_app.config["RATE_PER_DAY"],
                rented_by=g.user.uuid,
                uuid=str(uuid.uuid1()),
            )

            db.session.add(transaction)
            db.session.commit()

            if transaction:
                flash(f"'{book.name}' Issued!")

            return redirect(url_for("members_retrieve", id=str(member.uuid)))
