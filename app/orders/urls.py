from django.urls import path

from .views import dashboard_order_create, dashboard_order_edit, dashboard_orders


urlpatterns = [
    path("dashboard/orders/", dashboard_orders, name="dashboard_orders"),
    path("dashboard/orders/new/", dashboard_order_create, name="dashboard_order_create"),
    path("dashboard/orders/<int:pk>/edit/", dashboard_order_edit, name="dashboard_order_edit"),
]
