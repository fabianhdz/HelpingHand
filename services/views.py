from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, PostForm
from django.contrib.auth.decorators import login_required
from .models import Service, Post, Location, Role
from django.utils import timezone



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


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)

                return redirect('home')  # Redirect after successful signup
            else:
                messages.warning(request, 'Account failed to create')
                for field, error in form.errors.items():
                    messages.error(request, f"{field}: {error}")
        else:
            form = SignUpForm()
        return render(request, 'signup.html', {'form': form})


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
