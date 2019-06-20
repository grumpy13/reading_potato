from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegister, UserLogin

def register(request):
	form = UserRegister()
	if request.method == 'POST':
		form = UserRegister(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.set_password(user.password)
			user.save()
			login(request, user)
			return redirect("main:articles-list")
	context = {
        "form":form
    }
	return render(request, 'register.html', context)

def signin(request):
	form = UserLogin()
	if request.method == "POST":
		form = UserLogin(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']

			auth_user = authenticate(username=username, password=password)
			if auth_user is not None:
				login(request, auth_user)
				return redirect('main:articles-list')
	context = {
        "form":form
    }
	return render(request, 'signin.html', context)

def signout(request):
	logout(request)
	return redirect('main:articles-list')