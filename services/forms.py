from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class SignUpForm(UserCreationForm):
    phone = forms.CharField(required=True)
    language = forms.CharField(required=True)
    address = forms.CharField(required=True)
    zip_code = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        if commit:
            user.save()
            profile = Profile(user=user, phone=self.cleaned_data['phone'],
                              language=self.cleaned_data['language'],
                              address=self.cleaned_data['address'],
                              zip_code=self.cleaned_data['zip_code'])
            profile.save()
        return user
