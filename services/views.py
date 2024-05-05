from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserForm, PostForm, ProfileForm, PostFilterForm, RatingForm
from django.contrib.auth.decorators import login_required
from .models import Service, Location, Role, Skill, Post, Appointment, Profile, Language
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponseForbidden


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
                language_names = profile_form.cleaned_data['languages']
                # Create and save the profile linked to the user
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                for skill_name in skill_names:
                    skill, _ = Skill.objects.get_or_create(name=skill_name.capitalize())
                    profile.skills.add(skill)
                    user.skills.add(skill)
                profile_form.save_m2m()
                for language_name in language_names:
                    language, _ = Language.objects.get_or_create(name=language_name.capitalize())
                    profile.languages.add(language)
                    user.languages.add(language)
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
            location = Location.objects.filter(
                                    street_address=form.cleaned_data.get('street_address'),
                                    city=form.cleaned_data.get('city'),
                                    state=form.cleaned_data.get('state'),
                                    postal_code=form.cleaned_data.get('postal_code'),
                                    country=form.cleaned_data.get('country')
                                ).first()
            if not location:
                location = Location.objects.create(
                    street_address=form.cleaned_data.get('street_address'),
                    city=form.cleaned_data.get('city'),
                    state=form.cleaned_data.get('state'),
                    postal_code=form.cleaned_data.get('postal_code'),
                    country=form.cleaned_data.get('country')
                )

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


@login_required
def posts_feed(request):
    form = PostFilterForm(request.GET)
    #active_appointments = Appointment.objects.exclude(status='completed').values('post')
    posts = Post.objects.filter(is_active=True,).exclude(user=request.user)  # Only fetch active posts

    if form.is_valid():
        posts = form.filter_query(posts)
    posts = posts.filter(is_active=True)
    return render(request, 'posts_feed.html', {
        'form': form,
        'posts': posts
    })


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post_detail.html', {'post': post})


@login_required
def make_appointment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.user:
        return HttpResponseForbidden("You cannot make an appointment for your own post.")
    if post.is_active:
        appointment = Appointment.objects.create(user=request.user, post=post)
        post.is_active = False
        post.save()
        return redirect('appointment_confirmation', appointment_id=appointment.id)
    else:
        return redirect('post_detail', post_id=post_id)


@login_required
def appointment_confirmation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    post_user = appointment.post.user
    profile = getattr(post_user, 'profile', None)  # Safely get profile if exists
    return render(request, 'appointment_confirmation.html', {
        'appointment': appointment,
        'profile': profile
    })


@login_required
def my_posts(request):
    # Assuming each post has a 'user' ForeignKey to User
    posts = Post.objects.filter(user=request.user)
    return render(request, 'my_posts.html', {'posts': posts})


@login_required
def my_appointments(request):
    # Filter out completed appointments
    appointments = Appointment.objects.filter(user=request.user, status='active')
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if 'cancel' in action:
            appointment_id = action.split('_')[1]
            appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
            appointment.status = 'cancelled'  # Update status instead of deleting
            appointment.post.is_active = True
            appointment.post.save()
            appointment.save()
            return redirect('posts_feed')
        elif 'complete' in action:
            appointment_id = action.split('_')[1]
            return redirect('complete_appointment', appointment_id=appointment_id)

    return render(request, 'my_appointments.html', {'appointments': appointments})



@login_required
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.user != appointment.user:
        return redirect('home')  # Or handle permission error
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = appointment.post.user  # Assuming the post's user is the one being rated
            rating.appointment = appointment
            rating.save()
            appointment.status = 'completed'  # Mark as completed
            appointment.save()
            return redirect('posts_feed')
    else:
        form = RatingForm()

    return render(request, 'rate_user.html', {'form': form, 'appointment': appointment})


@login_required
def view_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)  # Get the profile associated with the user
    languages = profile.languages.all()
    skills = profile.skills.all()  # Get skills from the Profile's many-to-many relationship
    return render(request, 'profile.html', {
        'user': user,
        'profile': profile,
        'skills': skills,
        'languages': languages,
    })