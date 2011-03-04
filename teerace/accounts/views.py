from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import (authenticate, login as auth_login,
	logout as auth_logout)
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.views.generic.list_detail import object_list
from accounts.forms import (LoginForm, RegisterForm, SettingsUserForm,
	SettingsProfileForm, PasswordChangeForm)
from accounts.models import UserProfile
from race.models import Run
from annoying.functions import get_config
from annoying.decorators import render_to


@render_to('accounts/login.html')
def login(request):
	if request.user.is_authenticated():
		return redirect(reverse('home'))

	next_uri = request.REQUEST.get('next', get_config('LOGIN_REDIRECT_URL',
		reverse('home')))
	# rescuing poor users from infinite redirection loop
	if next_uri == get_config('LOGIN_URL', reverse('login')):
		next_uri = get_config('LOGIN_REDIRECT_URL', reverse('home'))

	login_form = LoginForm()

	if request.method == 'POST':
		login_form = LoginForm(request.POST)
		if login_form.is_valid() and login_form.user:
			auth_login(request, login_form.user)
			messages.success(request, "Hello, {0}.".format(login_form.user))
			return redirect(next_uri)

	return {
		'login_form': login_form,
		'next': next_uri,
	}


@login_required
def logout(request):
	next_uri = request.REQUEST.get('next', reverse('home'))
	auth_logout(request)
	messages.success(request, "Bye bye.")
	return redirect(next_uri)


@render_to('accounts/register.html')
def register(request):
	if request.user.is_authenticated():
		return redirect(reverse('home'))

	next_uri = request.REQUEST.get('next', get_config('FIRST_LOGIN_REDIRECT_URL',
		reverse('first_steps')))
	# rescuing poor users from infinite redirection loop
	if next_uri == get_config('LOGIN_URL', reverse('login')):
		next_uri = get_config('FIRST_LOGIN_REDIRECT_URL',
			reverse('first_steps'))

	register_form = RegisterForm()

	if request.method == 'POST':
		register_form = RegisterForm(request.POST)
		if register_form.is_valid():
			register_form.save()
			username = register_form.cleaned_data['username']
			password = register_form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			if user is not None:
				auth_login(request, user)
				messages.success(request, "Welcome aboard, {0}.".format(user))
			return redirect(next_uri)

	return {
		'register_form': register_form,
		'next': next_uri,
	}


@render_to('static/first_steps.html')
def first_steps(request):
	return {

	}


@render_to('accounts/welcome.html')
def welcome(request):
	return {

	}


@render_to('accounts/userprofile_detail.html')
def profile(request, user_id):
	if int(user_id) == 0:
		raise Http404 # mkay, no Anonymous profile
	user_profile = get_object_or_404(UserProfile.objects.select_related(), pk=user_id)
	user_runs = Run.objects.filter(user=user_id).order_by('-created_at')[:5]

	return {
		'profile': user_profile,
		'user_runs': user_runs,
	}


def userlist(request):
	# exclude anonymous
	# UPDATED also excluding banned players
	profiles = UserProfile.objects.exclude(user__is_active=False).select_related()
	return object_list(request, queryset=profiles)


@login_required
@render_to('accounts/api_token.html')
def api_token(request):
	# api_token is accessible in `user` template variable
	if request.method == 'POST':
		request.user.profile.regenerate_token()
		messages.success(request, "New API token has been generated."
			" Please update your game configuration file.")
	messages.info(request, "API token is required to log in the game."
		" You have to keep it secret!")
	messages.warning(request, "<b>Make sure you want to do this!</b>"
		" No, really. We will change your token (and disable current one).",
		extra_tags="hide")
	return {

	}


@login_required
@render_to('accounts/settings.html')
def settings(request):
	settings_user_form = SettingsUserForm(instance=request.user)
	settings_profile_form = SettingsProfileForm(instance=request.user.profile)
	if request.method == 'POST':
		settings_user_form = SettingsUserForm(request.POST, instance=request.user)
		settings_profile_form = SettingsProfileForm(request.POST,
			instance=request.user.profile)
		if settings_user_form.is_valid() and settings_profile_form.is_valid():
			settings_user_form.save()
			settings_profile_form.save()
			messages.success(request, "Successfully updated your profile and settings.")
	return {
		'settings_user_form': settings_user_form,
		'settings_profile_form': settings_profile_form,
	}


@login_required
@render_to('accounts/password_change.html')
def password_change(request):
	form = PasswordChangeForm(current_user=request.user)
	if request.method == 'POST':
		form = PasswordChangeForm(request.POST, current_user=request.user)
		if form.is_valid():
			form.save()
			messages.success(request, "Successfully changed your password.")
	messages.warning(request, "<b>Make sure you want to do this!</b>"
		" No, really. This action will change your password.",
		extra_tags="hide")
	return {
		'form': form,
	}