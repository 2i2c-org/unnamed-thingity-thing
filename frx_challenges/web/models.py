from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models.fields.json import KT
from django_jsonform.models.fields import JSONField

# Create your models here.


class Team(models.Model):
    name = models.CharField(max_length=1024)
    members = models.ManyToManyField(
        User, through="TeamMembership", related_name="teams"
    )


class Submission(models.Model):
    """
    A submission can be a collection of versions.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024, default="My model name")
    description = models.CharField(max_length=2048, default="My model description")
    date_created = models.DateTimeField(auto_now=True)
    # FIXME: A default for the team had to be provided
    # but because there was no default team, it was set to None
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name="projects",
    )
    metadata = JSONField(
        blank=True, null=True, schema=settings.SITE_SUBMISSION_FORM_SCHEMA
    )
    toc_accepted = models.BooleanField()

    @property
    def best_version(self) -> Version:
        """
        Return the 'best' evaluated version for this Submission
        """
        # Construct a query that returns evaluations that:
        # 1. Belong to a version that belong to this submission
        # 2. Have been succesfully evaluated
        # 3. Have results that contain all the keys we use for ordering
        # 4. Ordered by the ordering criteria expressed by EVALUATION_DISPLAY_CONFIG

        # Sort the display_config by ordering_priority (smaller numbers go first)
        # This primarily is used for tiebreaking, since we only want the 'best'
        sorted_display_config = sorted(
            settings.EVALUATION_DISPLAY_CONFIG, key=lambda dc: -dc["ordering_priority"]
        )

        # Ordering criteria for querying our results
        ordering_criteria = []
        # List of keys that *must* be present in a result for it to count
        result_must_have_keys = []

        for dc in sorted_display_config:
            result_must_have_keys.append(dc["result_key"])
            k = KT(f"result__{dc['result_key']}")
            if dc["ordering"] == "smaller_is_better":
                k = k.asc()
            elif dc["ordering"] == "bigger_is_better":
                k = k.desc()
            else:
                raise ValueError(
                    f"Invalid ordering {dc['ordering']} found for result_key {dc['result_key']}"
                )
            ordering_criteria.append(k)

        best_evaluation = (
            Evaluation.objects.filter(
                version__submission=self,
                status=Evaluation.Status.EVALUATED,
                result__has_keys=result_must_have_keys,
            )
            .order_by(*ordering_criteria)
            .first()
        )

        if best_evaluation:
            return best_evaluation.version


class Version(models.Model):
    """
    A version of a submission.
    """

    class Status(models.TextChoices):
        NOT_STARTED = "NOT_STARTED"
        UPLOADING = "UPLOADING"
        UPLOADED = "UPLOADED"
        CLEARED = "CLEARED"

    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="versions"
    )
    date_created = models.DateTimeField(auto_now=True)
    # FIXME: Cascade is probably not quite right?
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=1024)
    # FIXME: Figure out max_length
    data_uri = models.CharField(max_length=4096)
    # FIXME: Figure out max_length or use IntChoices
    status = models.CharField(choices=Status, default=Status.NOT_STARTED, max_length=16)

    @property
    def latest_evaluation(self) -> Evaluation | None:
        """
        Return the latest Evaluation if it exists
        """
        try:
            return self.evaluations.latest("last_updated")
        except Evaluation.DoesNotExist:
            return None

    def __str__(self):
        return f"({self.status}) {self.data_uri}"


class Evaluation(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = "NOT_STARTED"
        EVALUATING = "EVALUATING"
        EVALUATED = "EVALUATED"
        HIDDEN = "HIDDEN"
        FAILED = "FAILED"

    version = models.ForeignKey(
        Version, on_delete=models.CASCADE, related_name="evaluations"
    )
    evaluator_state = models.JSONField(default=dict)
    result = models.JSONField(blank=True, null=True)
    # FIXME: Figure out max_length or use IntChoices
    status = models.CharField(choices=Status, default=Status.NOT_STARTED, max_length=16)

    last_updated = models.DateTimeField(auto_now=True)

    @property
    def ordered_results(self) -> list:
        """
        Return results of this evaluation, ordered per EVALUATION_DISPLAY_CONFIG
        """
        results_list = []
        for cf in settings.EVALUATION_DISPLAY_CONFIG:
            if self.result:
                results_list.append(self.result.get(cf["result_key"]))
            else:
                results_list.append(None)
        return results_list

    def __str__(self):
        return f"({self.status}) {self.result} {self.version.data_uri}"


class TeamMembership(models.Model):
    is_admin = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")

    class Meta:
        # A user can be added to a team only once
        unique_together = ("user", "team")


class Page(models.Model):
    class MimeType(models.TextChoices):
        markdown = "text/markdown"
        html = "text/html"

    title = models.CharField(max_length=1024)
    slug = models.SlugField(
        max_length=128, help_text="Slug used to refer to this page's URL"
    )
    order = models.IntegerField(
        unique=True, help_text="Ordering of this page on the navbar"
    )
    is_home = models.BooleanField(
        default=False,
        help_text="Use current page as the home page. Only one page can have this enabled at any given time",
    )
    mimetype = models.CharField(
        default=MimeType.markdown,
        help_text="Mimetype used to render this page",
        max_length=32,
        choices=MimeType,
    )

    content = models.TextField(help_text="Markdown specifying the page's content")

    header_content = models.TextField(
        help_text="Content to use as page header", null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if not self.is_home:
            return super().save(*args, **kwargs)
        with transaction.atomic():
            Page.objects.filter(is_home=True).update(is_home=False)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ContentFile(models.Model):
    """
    Files (like images, object files, etc) to be used when constructing pages
    """

    title = models.CharField(max_length=1024)
    slug = models.SlugField(
        max_length=128, help_text="Slug used to refer to this image", unique=True
    )
    file = models.FileField(upload_to="content-files/%Y/%m/%d/")

    def __str__(self):
        return self.title
