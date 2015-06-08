#import factory
from ..models import NotificationRequest, SMSNotificationAssociation, EmailNotificationAssociation
from factory.django import DjangoModelFactory as ORMFactory


class SMSNotificationAssociationFactory(ORMFactory):
    FACTORY_FOR = SMSNotificationAssociation


class NotificationRequestFactory(ORMFactory):
    FACTORY_FOR = NotificationRequest


class EmailNotificationAssociationFactory(ORMFactory):
    FACTORY_FOR = EmailNotificationAssociation
