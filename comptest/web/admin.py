from allauth.account.decorators import secure_admin_login
from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import ContentFile, Evaluation, Page, Project, Submission


@admin.register(Page)
class PageAdmin(VersionAdmin):
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ContentFile)
class ContentFileAdmin(VersionAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register([Submission, Evaluation, Project])

admin.site.login = secure_admin_login(admin.site.login)