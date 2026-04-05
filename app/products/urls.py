from django.urls import path
from .views import product_price

urlpatterns = [
    path("api/product-price/<int:pk>/", product_price),
]