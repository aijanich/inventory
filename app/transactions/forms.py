from django import forms
from .models import ProductTransaction, Payment


class ProductTransactionForm(forms.ModelForm):
    class Meta:
        model = ProductTransaction
        exclude = ("date",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "client" in self.fields:
            self.fields["client"].queryset = self.fields["client"].queryset.exclude(user__is_staff=True)
        if "price" in self.fields:
            self.fields["price"].widget.attrs["readonly"] = "readonly"
            self.fields["price"].required = False
        if "total_amount" in self.fields:
            self.fields["total_amount"].widget.attrs["readonly"] = "readonly"
            self.fields["total_amount"].required = False
        if "quantity" in self.fields:
            self.fields["quantity"].widget.attrs["step"] = "1"


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        exclude = ("date",)


class ClientPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("amount", "note")
