from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.conf import settings
from django.urls import reverse
from django_jsonform.forms.fields import JSONFormField


class SubmissionForm(forms.Form):
    """Form to create a new submission"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = "submissions-create"
        self.helper.add_input(Submit("submit", "Submit", css_class="form-control"))

        self.fields["name"] = forms.CharField()
        self.fields["description"] = forms.CharField(required=False)
        self.fields["metadata"] = JSONFormField(
            schema=settings.SITE_SUBMISSION_FORM_SCHEMA
        )


class UploadForm(forms.Form):
    """Form to upload a version of a submission to be evaluated"""

    def __init__(self, id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = reverse("upload", args=[self.id])
        self.helper.add_input(Submit("submit", "Submit", css_class="form-control"))

        self.fields["file"] = forms.FileField()
        self.fields["file"].label = False


class TeamForm(forms.Form):
    """Form to create a new team"""

    def __init__(self, team_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.fields["name"] = forms.CharField(label="Team Name")
        self.helper.add_input(Submit("submit", "Submit", css_class="form-control"))


class AddMemberForm(forms.Form):
    """Form to add a member to a team"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.fields["username"] = forms.CharField(label="GitHub username")
        self.fields["is_admin"] = forms.BooleanField(required=False)
        self.helper.add_input(Submit("submit", "Add Member", css_class="form-control"))
