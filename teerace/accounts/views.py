from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from annoying.functions import get_config
from annoying.decorators import render_to
from accounts.forms import LoginForm, RegisterForm


@render_to('accounts/login.html')
def login(request, *args, **kwargs):
	if request.user.is_authenticated():
		return redirect(reverse('home'))

	next = request.REQUEST.get('next', get_config('LOGIN_REDIRECT_URL',
		reverse('accounts.views.welcome')))
	# rescuing poor users from infinite redirection loop
	if next == get_config('LOGIN_URL', reverse('login')):
		next = get_config('LOGIN_REDIRECT_URL', reverse('accounts.views.welcome'))

	login_form = LoginForm()

	if request.method == 'POST':
		login_form = LoginForm(request.POST)
		if login_form.is_valid() and login_form.user:
			auth_login(request, login_form.user)
			messages.success(request, "Hello, %s." % login_form.user)
			redirect(next)

	return {
		'login_form': login_form,
		'next': next,
	}


def logout(request, *args, **kwargs):
	next = request.REQUEST.get('next', reverse('home'))
	auth_logout(request)
	messages.success(request, "Bye bye.")
	return redirect(next)


@render_to('accounts/register.html')
def register(request, *args, **kwargs):
	if request.user.is_authenticated():
		return redirect(reverse('home'))

	next = request.REQUEST.get('next', get_config('FIRST_LOGIN_REDIRECT_URL',
		reverse('accounts.views.first_login')))
	# rescuing poor users from infinite redirection loop
	if next == get_config('LOGIN_URL', reverse('login')):
		next = get_config('FIRST_LOGIN_REDIRECT_URL',
			reverse('accounts.views.first_login'))

	register_form = RegisterForm()

	if request.method == 'POST':
		register_form = RegisterForm(request.POST)
		if register_form.is_valid():
			auth_login(request, register_form.save())
			messages.success(request, "Welcome aboard, %s." % login_form.user)
			redirect(next)

	return {
		'register_form': register_form,
		'next': next,
	}


@render_to('accounts/first_login.html')
def first_login(request, *args, **kwargs):
	return {
	
	}


@render_to('accounts/welcome.html')
def welcome(request, *args, **kwargs):
	return {
	
	}
