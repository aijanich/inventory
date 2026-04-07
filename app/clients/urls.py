from django.urls import path
from .views import (
    client_dashboard,
    dashboard_products,
    dashboard_payments,
    dashboard_payment_create,
    dashboard_product_create,
    dashboard_product_edit,
    dashboard_colors,
    dashboard_color_create,
    dashboard_color_edit,
    export_transactions_csv,
    export_transactions_pdf,
)

urlpatterns = [
    path("dashboard/", client_dashboard, name="client_dashboard"),
    path("dashboard/products/", dashboard_products, name="dashboard_products"),
    path("dashboard/products/new/", dashboard_product_create, name="dashboard_product_create"),
    path("dashboard/products/<int:pk>/edit/", dashboard_product_edit, name="dashboard_product_edit"),
    path("dashboard/colors/", dashboard_colors, name="dashboard_colors"),
    path("dashboard/colors/new/", dashboard_color_create, name="dashboard_color_create"),
    path("dashboard/colors/<int:pk>/edit/", dashboard_color_edit, name="dashboard_color_edit"),
    path("dashboard/payments/", dashboard_payments, name="dashboard_payments"),
    path("dashboard/payments/new/", dashboard_payment_create, name="dashboard_payment_create"),
    path("dashboard/transactions/export/csv/", export_transactions_csv, name="dashboard_transactions_export_csv"),
    path("dashboard/transactions/export/pdf/", export_transactions_pdf, name="dashboard_transactions_export_pdf"),
]
