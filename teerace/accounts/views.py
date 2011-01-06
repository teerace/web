from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import (authenticate, login as auth_login,
	logout as auth_logout)
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list
from accounts.forms import (LoginForm, RegisterForm, SettingsUserForm,
	SettingsProfileForm)
from accounts.models import UserProfile
from race.models import Run
from annoying.functions import get_config
from annoying.decorators import render_to


@render_to('accounts/login.html')
def login(request):
	if request.user.is_authenticated():
		return redirect(reverse('home'))

	next_uri = request.REQUEST.get('next', get_config('LOGIN_REDIRECT_URL',
		reverse('accounts.views.welcome')))
	# rescuing poor users from infinite redirection loop
	if next_uri == get_config('LOGIN_URL', reverse('login')):
		next_uri = get_config('LOGIN_REDIRECT_URL', reverse('accounts.views.welcome'))

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
		reverse('accounts.views.first_steps')))
	# rescuing poor users from infinite redirection loop
	if next_uri == get_config('LOGIN_URL', reverse('login')):
		next_uri = get_config('FIRST_LOGIN_REDIRECT_URL',
			reverse('accounts.views.first_steps'))

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
			redirect(next_uri)

	return {
		'register_form': register_form,
		'next': next_uri,
	}


@render_to('accounts/first_steps.html')
def first_steps(request):
	return {

	}


@render_to('accounts/welcome.html')
def welcome(request):
	return {

	}


@render_to('accounts/userprofile_detail.html')
def profile(request, user_id):
	profile = get_object_or_404(UserProfile.objects.select_related(), pk=user_id)
	user_runs = Run.objects.filter(user=user_id).order_by('-created_at')[:5]

	return {
		'profile': profile,
		'user_runs': user_runs,
	}


def userlist(request):
	# exclude anonymous
	profiles = UserProfile.objects.exclude(id=0).select_related()
	return object_list(request, queryset=profiles,
		paginate_by=get_config('ITEMS_PER_PAGE', 20))


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
			return redirect(reverse('settings'))
	return {
		'settings_user_form': settings_user_form,
		'settings_profile_form': settings_profile_form,
	}
