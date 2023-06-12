from library.members.views import (
    CreateMemberView,
    ListMemberView,
    RetrieveMemberView,
    UpdateMemberView,
    DeleteMemberView,
    IssueBookView,
)


def member_urls(app):
    app.add_url_rule("/members/", view_func=ListMemberView.as_view("members_list"))
    app.add_url_rule(
        "/members/create/", view_func=CreateMemberView.as_view("members_create")
    )
    app.add_url_rule(
        "/members/<uuid:id>/", view_func=RetrieveMemberView.as_view("members_retrieve")
    )
    app.add_url_rule(
        "/members/<uuid:id>/update/",
        view_func=UpdateMemberView.as_view("members_update"),
    )
    app.add_url_rule(
        "/members/<uuid:id>/delete/",
        view_func=DeleteMemberView.as_view("members_delete"),
    )
    app.add_url_rule(
        "/members/<uuid:id>/book-issue/",
        view_func=IssueBookView.as_view("member-books_issue"),
    )
