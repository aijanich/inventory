from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect


def home_redirect(request):
    if request.user.is_authenticated:
        is_admin = request.user.is_staff or getattr(request.user, "role", "") == "admin"
        if is_admin:
            return redirect("client_dashboard")
        if hasattr(request.user, "profile"):
            return redirect("client_dashboard")
        return redirect("login")
    return redirect("login")


urlpatterns = [
    path("", home_redirect),
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="clients/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("clients.urls")),
    path("", include("products.urls")),
    path("transactions/", include("transactions.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
