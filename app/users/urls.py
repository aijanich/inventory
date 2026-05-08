from django.urls import path

from .views import dashboard_users, dashboard_user_create, dashboard_user_edit

urlpatterns = [
    path("dashboard/users/", dashboard_users, name="dashboard_users"),
    path("dashboard/users/new/", dashboard_user_create, name="dashboard_user_create"),
    path("dashboard/users/<int:pk>/edit/", dashboard_user_edit, name="dashboard_user_edit"),
]

