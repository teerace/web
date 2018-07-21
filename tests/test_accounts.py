import pytest

from accounts.forms import LoginForm, RegisterForm


@pytest.fixture()
def regularuser(django_user_model):
    user = django_user_model(username="test", is_superuser=False)
    user.set_password("test")
    user.save()
    return user


@pytest.fixture()
def data():
    return {
        "username": "new",
        "password1": "test123",
        "password2": "test123",
        "email1": "testclient@example.com",
        "email2": "testclient@example.com",
    }


@pytest.mark.django_db
def test_register_form_passwords_dont_match(data):
    form = RegisterForm({**data, "password2": "mismatched"})
    assert not form.is_valid()
    assert form["password2"].errors == ["You must type the same password each time"]


@pytest.mark.django_db
def test_register_form_user_already_exists(data, regularuser):
    form = RegisterForm({**data, "username": "test"})
    assert not form.is_valid()
    assert form["username"].errors == ["Username is already taken"]


@pytest.mark.django_db
def test_register_form_emails_dont_match(data):
    form = RegisterForm({**data, "email2": "mismatched@example.com"})
    assert not form.is_valid()
    assert form["email2"].errors == ["You must type the same e-mail address each time"]


@pytest.mark.django_db
def test_register_form_user_created(data, regularuser, django_user_model):
    form = RegisterForm(data)
    assert form.is_valid()
    form.save()
    assert django_user_model.objects.filter(username="new").exists()


@pytest.mark.django_db
def test_login_form_wrong_username(regularuser):
    form = LoginForm({"username": "wrong", "password": "test"})
    assert not form.is_valid()
    assert form.errors["__all__"] == ["Invalid username and/or password"]


@pytest.mark.django_db
def test_login_form_success(regularuser):
    form = LoginForm({"username": "test", "password": "test"})
    assert form.is_valid()
