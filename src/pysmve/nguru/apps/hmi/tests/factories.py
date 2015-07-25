from factory.django import DjangoModelFactory as ORMFactory
from django.contrib.auth.models import User


class UserFactory(ORMFactory):
    class Meta:
        model = User

    @classmethod
    def _generate(cls, create, attrs):
        password = attrs.pop('password', attrs['username'])
        user = super(UserFactory, cls)._generate(create, attrs)
        user.set_password(password)
        user.save()
        return user
