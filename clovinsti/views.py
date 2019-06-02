from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from . import settings
from .forms import LoginForm, SignupForm
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.urls import reverse
import json

# def home_page(request):
#     return render(request, "home.html",{"brand":settings.brand_name, "title": "ClovInsti"})

def home_page(request):
    # View code here...
    return redirect(reverse('course_list'), {"brand":settings.brand_name, "title": "ClovInsti"})

def login_page(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            uname = form.cleaned_data.get('username')
            passwd = form.cleaned_data.get('password')
            user = authenticate(request, username=uname, password=passwd)
            if user is not None:
                login(request, user)
                print(f"User is logged in {user}")

                next_page = request.GET.get('next')
                if next_page:
                    return HttpResponseRedirect(next_page)
                else:    
                    # redirect to a new URL:
                    return HttpResponseRedirect(reverse('home_page'))
            else:
                print("User authentication failed")
    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()
    
    context = {
        "brand":settings.brand_name, 
        "title": "ClovInsti",
        "form": form,
        }
    return render(request, 'auth/login.html', context)



User = get_user_model()
def signup_page(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SignupForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            uname = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            passwd = form.cleaned_data.get('password')
            new_user = User.objects.create_user(uname, email, passwd)
            print(new_user)
            return HttpResponseRedirect(reverse('login_page'))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = SignupForm()
    
    context = {
        "brand":settings.brand_name, 
        "title": "ClovInsti",
        "form": form,
        }
    return render(request, 'auth/signup.html', context)    

def logout_page(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect(reverse('login_page'))

def login_ajax(request):
    # process the data in form.cleaned_data as required
    uname = request.POST.get('username', None)
    passwd = request.POST.get('password',None)
    user = authenticate(request, username=uname, password=passwd)
    resp = None
    if user is not None:
        login(request, user)
        resp = str(user)
        print(f"Ajax User is logged in {resp}")
        # redirect to a new URL:
    else:
        print("Ajax User authentication failed")
    
    return HttpResponse(json.dumps({'user': resp}), content_type="application/json")
