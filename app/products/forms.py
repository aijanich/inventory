from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("client", "name", "code", "price", "comment", "image")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "client" in self.fields:
            self.fields["client"].queryset = self.fields["client"].queryset.exclude(user__is_staff=True)
