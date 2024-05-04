from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserForm, PostForm, ProfileForm
from django.contrib.auth.decorators import login_required
from .models import Service, Location, Role, Skill
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction


def home(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful, Welcome Back")
            return redirect('home')
        else:
            messages.success(request, "An Error Occured, Please Login Again")
            return redirect('home')
    else:
        return render(request, 'home.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, "You logged out successfully")
    return redirect('home')


def signup_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            # Store the validated user data in session to use in the next step
            request.session['user_data'] = user_form.cleaned_data
            # Redirect to the profile completion step
            return redirect('signup_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserForm()
    return render(request, 'signup_user.html', {'user_form': user_form})


def signup_profile(request):
    if 'user_data' not in request.session:
        # If there is no user data in the session, redirect to the initial signup form.
        return redirect('signup_user')

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST)
        if profile_form.is_valid():
            with transaction.atomic():  # Start of transaction
                # Retrieve user data from session and remove the session data
                user_data = request.session.pop('user_data', None)
                # Create the user instance but don't save it to the DB yet
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                user.set_password(user_data['password1'])  # Set and hash the password
                user.save()  # Save the user to the database
                skill_names = profile_form.cleaned_data['skills']
                # Create and save the profile linked to the user
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                for skill_name in skill_names:
                    skill, _ = Skill.objects.get_or_create(name=skill_name.capitalize())
                    profile.skills.add(skill)
                    user.skills.add(skill)
                profile_form.save_m2m()  # Save many-to-many relationships if applicable

                # Optionally log in the new user
                login(request, user)

            # If everything is successful, show a success message and redirect
            messages.success(request, 'Account successfully created.')
            return redirect('home')
        else:
            # If the form is not valid, return with error messages
            messages.error(request, 'Please correct the errors below.')
    else:
        # If it's a GET request, just render the form
        profile_form = ProfileForm()

    return render(request, 'signup_profile.html', {'profile_form': profile_form})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():

            service_name = form.cleaned_data.get('service')
            service, _ = Service.objects.get_or_create(name=service_name.capitalize())
            location, _ = Location.objects.get_or_create(
                            street_address=form.cleaned_data.get('street_address'),
                            city=form.cleaned_data.get('city'),
                            state=form.cleaned_data.get('state'),
                            postal_code=form.cleaned_data.get('postal_code'),
                            country=form.cleaned_data.get('country'))

            role_name = form.cleaned_data.get('role')
            role, _ = Role.objects.get_or_create(name=role_name.capitalize())
            post = form.save(commit=False)
            post.role = role
            post.location = location
            post.service = service
            post.user = request.user
            post.date = timezone.now()
            post.save()
            form.save_m2m()  # Save any many-to-many relationships

            return redirect('home')  # Redirect to a home or another appropriate view
        else:
            messages.error(request, "There were errors in your form submission.")
    else:
        form = PostForm()

    return render(request, 'create_post.html', {'form': form})
