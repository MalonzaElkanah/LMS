from flask.views import View
from flask import render_template

from library.utils import login_required


class IndexView(View):
    methods = [
        "GET",
    ]
    decorators = [
        login_required,
    ]

    def dispatch_request(self):
        return render_template("index.html", title="KNLS Library System")
