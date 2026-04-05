from django.http import JsonResponse
from .models import Product


def product_price(request, pk):
    product = Product.objects.get(pk=pk)
    return JsonResponse({
        "price": product.price
    })