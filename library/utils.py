import functools
from flask import g, session, redirect, url_for
from library.models import User


def before_request(app):
    """
    Code to be Executed for each request before the view
    """

    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")

        if user_id is None:
            g.user = None
        else:
            g.user = User.query.filter_by(uuid=user_id).one_or_none()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("user_login"))

        return view(*args, **kwargs)

    return wrapped_view
