from annoying.functions import get_config
from captcha.fields import ReCaptchaField
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import UserProfile


class RegisterForm(forms.Form):
    username = forms.RegexField(
        label="Username", regex=r"^\w+$", min_length=2, max_length=30
    )
    password1 = forms.CharField(
        label="Password",
        min_length=4,
        widget=forms.PasswordInput(render_value=False),
        help_text="At least 4 chars long",
    )
    password2 = forms.CharField(
        label="Password (again)",
        min_length=4,
        widget=forms.PasswordInput(render_value=False),
    )
    email1 = forms.EmailField(
        label="E-mail address", help_text="We won't share this to any 3rd-parties!"
    )
    email2 = forms.EmailField(label="E-mail address (again)")

    if get_config("ENABLE_CAPTCHA", False):
        recaptcha = ReCaptchaField(label="Human test", required=True)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        try:
            user = User.objects.get(username__iexact=username)
            del user
            raise forms.ValidationError("Username is already taken")
        except User.DoesNotExist:
            pass
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("You must type the same password each time")
        return password2

    def clean_email2(self):
        email1 = self.cleaned_data.get("email1")
        email2 = self.cleaned_data.get("email2")
        if email1 != email2:
            raise forms.ValidationError(
                "You must type the same e-mail address each time"
            )
        return email2

    def save(self):
        return User.objects.create_user(
            self.cleaned_data.get("username"),
            self.cleaned_data.get("email1"),
            self.cleaned_data.get("password1"),
        )


class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput(render_value=False)
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if not username or not password:
            return self.cleaned_data

        self.user = authenticate(username=username, password=password)
        if self.user == None:
            raise forms.ValidationError("Invalid username and/or password")
        if not self.user.is_active:
            raise forms.ValidationError("Your account has been disabled")
        return self.cleaned_data


class SettingsUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name")


class SettingsProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("gender", "country")


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label="Old password", widget=forms.PasswordInput(render_value=False)
    )
    new_password1 = forms.CharField(
        label="New password",
        min_length=4,
        widget=forms.PasswordInput(render_value=False),
    )
    new_password2 = forms.CharField(
        label="New password (again)",
        min_length=4,
        widget=forms.PasswordInput(render_value=False),
    )

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        if self.current_user is None:
            raise AttributeError("current_user missing")
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.current_user.check_password(old_password):
            raise forms.ValidationError("You have to type your old password correctly.")
        return old_password

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        if new_password1 != new_password2:
            raise forms.ValidationError("You must type the same password each time")
        return new_password2

    def save(self):
        self.current_user.set_password(self.cleaned_data.get("new_password1"))
        self.current_user.save()
