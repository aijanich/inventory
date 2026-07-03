from django import forms
from django.contrib.auth import get_user_model

from products.models import Product

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("user", "product", "color", "count", "sizes")
        labels = {
            "user": "Foydalanuvchi",
            "product": "Tovar",
            "color": "Rangi",
            "count": "Soni",
            "sizes": "O'lchamlari",
        }
        widgets = {
            "sizes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop("request_user", None)
        super().__init__(*args, **kwargs)

        is_admin = bool(
            request_user
            and (request_user.is_staff or getattr(request_user, "role", "") == "admin")
        )

        self.fields["user"].queryset = get_user_model().objects.exclude(is_staff=True)
        if not is_admin and request_user:
            self.fields["user"].queryset = get_user_model().objects.filter(pk=request_user.pk)
            self.fields["user"].initial = request_user
            self.fields["user"].disabled = True

        if not is_admin and request_user and hasattr(request_user, "profile"):
            self.fields["product"].queryset = Product.objects.filter(client=request_user.profile)
