from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ..forms import AddMemberForm, TeamForm
from ..models import Team, TeamMembership


@login_required
def list(request: HttpRequest) -> HttpResponse:
    """
    List all teams the current user is a member of
    """
    memberships = TeamMembership.objects.filter(user=request.user)
    return render(request, "teams/list.html", {"memberships": memberships})


@login_required
def create(request: HttpRequest) -> HttpResponse:
    """
    Create a new team with current user as admin
    """
    if request.method == "POST":
        form = TeamForm(data=request.POST)
        if form.is_valid():
            team = Team()
            team.name = form.cleaned_data["name"]
            # FIXME: Transactions?
            team.save()
            membership = TeamMembership()
            membership.user = request.user
            membership.team = team
            membership.is_admin = True
            membership.save()

            return HttpResponseRedirect(reverse("teams-view", args=[team.id]))
    else:
        form = TeamForm()

    return render(request, "teams/create.html", {"form": form})


# Intentionally not authenticated, as anyone should be able to view team membership
def view(request: HttpRequest, id: int) -> HttpResponse:
    """
    Display information about a particular team
    """
    try:
        team = Team.objects.filter(id=id).get()
    except Team.DoesNotExist:
        raise Http404("The requested team does not exist")

    # If logged in, check if user is admin on the team
    user_is_admin = False
    if request.user.is_authenticated:
        try:
            # FIXME: Turn `first` into `only` after adding appropriate constraints
            user_membership = TeamMembership.objects.filter(
                team=team, user=request.user
            ).first()
            user_is_admin = user_membership.is_admin
        except TeamMembership.DoesNotExist:
            # User is not part of the team
            pass

    return render(
        request, "teams/view.html", {"team": team, "user_is_admin": user_is_admin}
    )


@login_required
def add_member(request: HttpRequest, id: int) -> HttpRequest:
    try:
        team = Team.objects.filter(id=id).get()
    except Team.DoesNotExist:
        raise Http404("The requested team does not exist")

    # FIXME: Validate that we are admin on the team so we can add people
    # user = TeamMembership.objects.filter(team_id=id)
    # print(user)

    if request.method == "POST":
        form = AddMemberForm(request.POST)
        if form.is_valid():
            # Handle missing users
            try:
                user = User.objects.filter(username=form.cleaned_data["username"]).get()
            except User.DoesNotExist:
                raise Http404("The requested user does not exist")

            # FIXME: Handle an 'invitation acceptance' flow for users

            membership = TeamMembership()
            membership.user = user
            membership.team = team
            membership.is_admin = form.cleaned_data["is_admin"]
            membership.save()
            return HttpResponseRedirect(reverse("teams-view", args=(team.id,)))
        else:
            print("error")
    else:
        form = AddMemberForm()
        print("test")
    return render(request, "teams/add-member.html", {"form": form, "team": team})
