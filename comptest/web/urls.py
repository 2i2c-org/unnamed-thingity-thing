from django.urls import path

from .views import default, teams

urlpatterns = [
    path("upload", default.upload, name="upload"),
    path("results", default.results, name="results"),
    path("teams/list", teams.list, name="teams-list"),
    path("teams/create", teams.create, name="teams-create"),
    path("teams/<int:id>", teams.view, name="teams-view"),
    path("teams/<int:id>/add-member", teams.add_member, name="teams-add-member"),
    path("", default.home, name="home"),
]
