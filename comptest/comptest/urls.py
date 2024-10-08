from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from web.views.socialaccount import CustomLoginView

urlpatterns = [
    path("", include("web.urls")),
    path("admin/", admin.site.urls),
    path("accounts/login/", CustomLoginView.as_view(), name="account_login"),
    path("accounts/", include("allauth.urls")),
]

# Enable static serving even with external webserver like gunicorn
urlpatterns += staticfiles_urlpatterns()

# Serve media URLs only when running as debug mode
# nginx should serve them for us otherwise
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
