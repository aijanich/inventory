from django import forms
from .models import Color


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ("name", "code", "image", "comment")
