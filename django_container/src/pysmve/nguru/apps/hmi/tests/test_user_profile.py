# noqa
# User Profile
import pytest
from .factories import UserFactory
from apps.hmi.models import UserProfile
from django.core.urlresolvers import reverse
from fixtures import app  # pragma: no flakes


@pytest.mark.django_db
def test_user_has_profile():
    user = UserFactory(username="a_user")
    assert UserProfile.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_user_profile_validates_phone(app):   #
    staff = UserFactory(username="staff", is_superuser=True, is_staff=True)
    user_to_modify = UserFactory(username="cellphone_guy")
    url = reverse('admin:auth_user_change', args=(user_to_modify.pk, ))
    response = app.get(url, user=staff)
    PHONE = '5492804398772'
    response.form['userprofile_set-0-cellphone'] = PHONE
    response = response.form.submit('_save')
    assert user_to_modify.get_profile().cellphone == PHONE
