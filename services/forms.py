from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Location, Post, Role, Service


class UserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class ProfileForm(forms.ModelForm):
    street_address = forms.CharField(max_length=255, required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    postal_code = forms.CharField(max_length=20, required=True)
    country = forms.CharField(max_length=100, required=True)

    skills = forms.CharField(required=True, help_text="Enter skills separated by commas.")

    class Meta:
        model = Profile
        fields = ['phone', 'language']

    def clean_skills(self):
        skills_str = self.cleaned_data.get('skills', '')
        # Split the skills string by commas and strip spaces from each skill
        skill_names = [skill.strip() for skill in skills_str.split(',') if skill.strip()]
        return skill_names

    def save(self, commit=True):
        profile = super(ProfileForm, self).save(commit=False)
        # Ensure location creation and other settings are done here
        location = Location.objects.create(
            street_address=self.cleaned_data['street_address'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            postal_code=self.cleaned_data['postal_code'],
            country=self.cleaned_data['country']
        )
        profile.location = location

        if commit:
            profile.save()
        return profile


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
        fields = ['description', 'price_range', 'expiration_date']
        exclude = ['service', 'role', 'location']

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['role'].queryset = Role.objects.exclude(name='Admin')


class PostFilterForm(forms.Form):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False, label='Role')
    service = forms.ModelChoiceField(queryset=Service.objects.all(), required=False, label='Service')
    city = forms.CharField(max_length=100, required=False, label='City')
    state = forms.CharField(max_length=100, required=False, label='State')
    postal_code = forms.CharField(max_length=20, required=False, label='Postal Code')
    country = forms.CharField(max_length=100, required=False, label='Country')

    def filter_query(self, queryset):
        if self.cleaned_data['role']:
            queryset = queryset.filter(role=self.cleaned_data['role'])
        if self.cleaned_data['service']:
            queryset = queryset.filter(service=self.cleaned_data['service'])
        if self.cleaned_data['city']:
            queryset = queryset.filter(location__city__icontains=self.cleaned_data['city'])
        if self.cleaned_data['state']:
            queryset = queryset.filter(location__state__icontains=self.cleaned_data['state'])
        if self.cleaned_data['postal_code']:
            queryset = queryset.filter(location__postal_code=self.cleaned_data['postal_code'])
        if self.cleaned_data['country']:
            queryset = queryset.filter(location__country__icontains=self.cleaned_data['country'])
        return queryset
