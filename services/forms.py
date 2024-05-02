from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile ,Post, Service, Skill, Location, Role


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



class PostForm(forms.ModelForm):
    # Use ModelChoiceField to ensure the role is limited to 'Provider' or 'Client'
    ROLE_CHOICES = [
        ('Provider', 'Provider'),
        ('Client', 'Client'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    # Text field for service name
    service = forms.CharField(max_length=100, required=True)
    # Dynamic skills (handled by JavaScript in the frontend)
    # Standard fields
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True)
    price_range = forms.FloatField(required=True)
    expiration_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    street_address = forms.CharField(max_length=255, required=True, initial='')
    city = forms.CharField(max_length=100, required=True, initial='')
    state = forms.CharField(max_length=100, required=True, initial='')
    postal_code = forms.CharField(max_length=20, required=True, initial='')
    country = forms.CharField(max_length=100, required=True, initial='')

    class Meta:
        model = Post
        fields = [ 'description', 'price_range', 'expiration_date']
        exclude = ['service', 'role', 'location']

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['role'].queryset = Role.objects.exclude(name='Admin')  # Assuming 'Admin' is not a valid role for posting
