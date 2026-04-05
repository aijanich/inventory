from django.urls import path
from . import views

urlpatterns = [
    path("transaction/new/", views.create_transaction, name="create_transaction"),
    path("transaction/<int:pk>/edit/", views.edit_transaction, name="edit_transaction"),
    path("payment/<int:pk>/edit/", views.edit_payment, name="edit_payment"),
]
