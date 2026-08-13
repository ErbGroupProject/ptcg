from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages,auth
# from contacts.models import Contact
# Create your views here.
def register(request):
    if request.method =="POST":
        #Get form values
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        #check if passwords match
        if password == password2:
            #Check username
            if User.objects.filter(username=username).exists():
                messages.error(request,'That username is taken')
                return render(request,'accounts/register.html')
            else:
                if User.objects.filter(email=email.lower()).exists():
                    messages.error(request,'That email is being used')
                    return render(request,'accounts/register.html')
                else:
                    user= User.objects.create_user(
                        username=username,
                        email=email.lower(),
                        password=password,
                        first_name=first_name,
                        last_name=last_name)
                    user.save()
                    messages.success(request,'You are now registered and can log in')
                    return redirect('accounts:login')
                    #looks good
        else:
            messages.error(request,'Passwords do not match')
            return render(request,'accounts/register.html')
    else:
        return render(request,'accounts/register.html')

def login(request):
    if request.method =="POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            messages.success(request,'You are now logged in')
            return redirect('accounts:dashboard')
        else:
            messages.error(request,'Invalid credentials')
            return redirect('accounts:login')
    return render(request,'accounts/login.html')

def logout(request):
    if request.method =="POST":
        auth.logout(request)
    return redirect('pages:index')

def dashboard(request):
    user_contacts = Contact.objects.order_by(
        '-contact_date').filter(user_id=request.user.id)
    context = {"contacts":user_contacts}
    return render(request,'accounts/dashboard.html',context)
