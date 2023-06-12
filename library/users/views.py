from flask.views import View
from flask import (
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from marshmallow import ValidationError

from library.models import db, User
from library.users.schemas import UserRegisterSchema, UserLoginSchema
from library.utils import login_required


class CreateUserView(View):
    methods = ["GET", "POST"]

    _title = "Register User"
    _form = {"email": "email", "password": "password", "confirm_password": "password"}

    def dispatch_request(self):
        if request.method == "GET":
            if g.user is None:
                return render_template(
                    "forms.html", title=self._title, form=self._form, item={}
                )
            else:
                return render_template(
                    "info.html",
                    title=self._title,
                    message=f"""
                    Your are already logged in as {g.user.email}. Click here to
                    <a href="{url_for('user_logout')}">logout</a>.
                    """,
                )

        elif request.method == "POST":
            try:
                results = UserRegisterSchema().load(request.form)
            except ValidationError as error:
                print(error)
                for key, value in error.messages.items():
                    flash(f"{key}: {value[0]}")
                    break

                return render_template(
                    "forms.html", title=self._title, form=self._form, item=request.form
                )

            email = results.get("email")
            user = User(email=results.get("email"), password=results.get("password"))
            user.set_password(user.password)

            db.session.add(user)
            db.session.commit()

            user = User.query.filter_by(email=email).one_or_none()
            if user:
                return render_template(
                    "info.html",
                    title=f"{self._title} Success!",
                    message=f"""
                    User Created. Please follow this
                    <a href="{url_for('user_login')}"> link to login</a>.
                    """,
                )
            else:
                return render_template(
                    "info.html",
                    title=self._title,
                    message="Error Creating user. Please try again later.",
                )


class LoginUserView(View):
    methods = ["GET", "POST"]

    _title = "Login"
    _form = {"email": "email", "password": "password"}

    def dispatch_request(self):
        if request.method == "GET":
            # Check if user logged in
            if g.user is None:
                return render_template(
                    "forms.html", title=self._title, form=self._form, item={}
                )
            else:
                return render_template(
                    "info.html",
                    title=self._title,
                    message=f"""
                    Your are already logged in as {g.user.email}. Click here to
                    <a href="{url_for('user_logout')}">logout</a>.
                    """,
                )
        elif request.method == "POST":
            print(request.form)
            errors = UserLoginSchema().validate(request.form)
            print(errors)
            for key, value in errors.items():
                flash(f"{key}: {value}")
                return render_template(
                    "forms.html", title=self._title, form=self._form, item=request.form
                )
                break

            results = request.form

            if results.get("email", None):
                user = User.query.filter_by(email=results["email"]).one_or_none()

                if user is not None:
                    if user.verify_password(results["password"]):
                        session.clear()
                        session["user_id"] = user.uuid
                        return redirect("../../")

            flash("Incorrect username or password.")
            return render_template(
                "forms.html", title=self._title, form=self._form, item=request.form
            )


class LogoutUserView(View):
    methods = [
        "GET",
    ]
    decorators = [
        login_required,
    ]

    def dispatch_request(self):
        session.clear()
        return redirect("/users/login/")
