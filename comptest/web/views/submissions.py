from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ..models import Evaluation


@login_required
def list(request: HttpRequest) -> HttpResponse:
    """
    List all evaluations of the current user
    """
    submissions = Evaluation.objects.filter(submission__user=request.user)
    return render(request, "submissions.html", {"submissions": submissions})
