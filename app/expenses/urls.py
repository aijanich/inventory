from django.urls import path

from .views import dashboard_expenses, dashboard_expense_create, dashboard_expense_edit

urlpatterns = [
    path("dashboard/expenses/", dashboard_expenses, name="dashboard_expenses"),
    path("dashboard/expenses/new/", dashboard_expense_create, name="dashboard_expense_create"),
    path("dashboard/expenses/<int:pk>/edit/", dashboard_expense_edit, name="dashboard_expense_edit"),
]

