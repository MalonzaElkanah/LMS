from library.users.views import CreateUserView, LoginUserView, LogoutUserView


def user_urls(app):
    app.add_url_rule(
        "/users/register/", view_func=CreateUserView.as_view("user_register")
    )
    app.add_url_rule("/users/login/", view_func=LoginUserView.as_view("user_login"))
    app.add_url_rule("/users/logout/", view_func=LogoutUserView.as_view("user_logout"))
