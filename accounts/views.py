from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth.forms import UserChangeForm
from .forms import ProfileForm



@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

# 新增
@login_required
def profile(request):
    return render(request, "accounts/profile.html")
@login_required

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "accounts/edit_profile.html", {"form": form})

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'That username is taken')
                return redirect('accounts:register')
            else:
                if User.objects.filter(email=email.lower()).exists():
                    messages.error(request, 'That email is being used')
                    return redirect('accounts:register')
                else:
                    User.objects.create_user(
                        username=username,
                        email=email.lower(),
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    messages.success(request, 'You are now registered and can log in')
                    return redirect('accounts:login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('accounts:register')
    else:
        return render(request, 'accounts/register.html')


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'User name or password does not right! Plesae try again!')
            return redirect('accounts:login')
    return render(request, 'accounts/login.html')


def logout(request):
    if request.method == "POST":
        auth.logout(request)
        return redirect('pages:index')
    return redirect('pages:index')