from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm


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
