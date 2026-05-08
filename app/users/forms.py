from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from clients.models import ClientProfile

User = get_user_model()


class ClientUserCreateForm(UserCreationForm):
    phone = forms.CharField(max_length=20)
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "phone", "address", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "client"
        user.is_staff = False
        if commit:
            user.save()
            ClientProfile.objects.create(
                user=user,
                phone=self.cleaned_data["phone"],
                address=self.cleaned_data["address"],
            )
        return user


class ClientUserUpdateForm(forms.ModelForm):
    phone = forms.CharField(max_length=20)
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "is_active")

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop("profile", None)
        super().__init__(*args, **kwargs)
        if self.profile is not None:
            self.fields["phone"].initial = self.profile.phone
            self.fields["address"].initial = self.profile.address

    def save(self, commit=True):
        user = super().save(commit=commit)
        if self.profile is not None:
            self.profile.phone = self.cleaned_data["phone"]
            self.profile.address = self.cleaned_data["address"]
            if commit:
                self.profile.save()
        return user

