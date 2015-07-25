from ..models import (
    NotificationRequest, SMSNotificationAssociation, EmailNotificationAssociation,
)
from factory.django import DjangoModelFactory as ORMFactory


class SMSNotificationAssociationFactory(ORMFactory):
    class Meta:
        model = SMSNotificationAssociation


class NotificationRequestFactory(ORMFactory):
    class Meta:
        model = NotificationRequest


class EmailNotificationAssociationFactory(ORMFactory):
    class Meta:
        model = EmailNotificationAssociation
