# -*- coding: utf-8 -*-
from django import VERSION
from django.db import models
from apps.mara.models import DI, Event
from django.contrib.auth.models import User
from django.db.models import signals
from django.dispatch import receiver
from datetime import datetime
from .validators import validate_template_format
from django.template import Context, Template
from mailer.models import Message
from .fields import  CommaSeparatedEmailField
from django.conf import settings


if VERSION <= (1, 7):
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.contenttypes import generic
else:
    from django.contrib.contenttypes.fields import GenericForeignKey
    from django.contrib.contenttypes.models import ContentType


class BaseNotificationAssociation(models.Model):
    name = models.CharField(
        verbose_name="Nombre de Regla",
        max_length=100,
        unique=True,
    )

    targets = models.ManyToManyField(
        User,
        verbose_name=u"Destinatarios",
        help_text="Solo se muestran los usuarios que tengan un nro. de celular cargado."
    )

    template = models.TextField(
        verbose_name="Plantilla",
        validators=[validate_template_format, ],
        default="{{ event }} {{ timestamp }}",
        help_text="Ver referencia en <a href='https://docs.djangoproject.com"
        "/en/1.8/ref/templates/builtins/' target='_blank'>Documentación Django</a>"
    )

    def render_template(self, event):
        template = Template(self.template)
        context = Context({
            'event': event,
            'association': self,
        }, use_l10n=True)

        text = template.render(context)
        return text

    def __unicode__(self):
        return self.name


    class Meta:
        abstract = True

    @classmethod
    def apply_for_qs(cls, qs):
        raise NotImplementedError("Not implemented for base class")

    def create_for_event(self, event):
        raise NotImplementedError("Not implemented for base class")


class SMSNotificationAssociation(BaseNotificationAssociation):
    """
    Rules of notifications to be created when a Event is saved into DB
    """

    source_di = models.ManyToManyField(
        DI,
        verbose_name=u"Fuentes de notificación",
        related_name='sms_associations'
    )

    class Meta:
        verbose_name = u"Regla de Envío de SMS"
        verbose_name_plural = u"Reglas de Envíos de SMS"

    @classmethod
    def create_for_event(cls, event):
        """Called from event hook, receives an instance"""
        print cls
        created_notifications_pks = set()
        for notification_assoc in event.di.sms_associations.all():
            for user in notification_assoc.targets.all():

                body = notification_assoc.render_template(event=event)

                created = NotificationRequest.objects.create(
                    status=NotificationRequest.STATUS_CREATED,
                    last_status_change_time=datetime.now(),
                    destination=user.get_profile().cellphone,
                    body=body,
                    source=event,
                )
                created_notifications_pks.add(created.pk)
        return NotificationRequest.objects.filter(pk__in=created_notifications_pks)

    def apply_for_qs(cls, qs):
        qs = NotificationRequest.objects.none()
        for event in qs:
            qs |= cls.create_for_event(event)


class EmailNotificationAssociation(BaseNotificationAssociation):

    source_di = models.ManyToManyField(
        DI,
        verbose_name=u"Fuentes de notificación",
        related_name='email_associations'
    )

    subject = models.TextField(
        default='Alerta SMVE',
        verbose_name='Asunto'
    )

    cc = CommaSeparatedEmailField(
        blank=True,
        null=True,
        verbose_name='Copia Carbónica',
    )

    bcc = CommaSeparatedEmailField(
        blank=True,
        null=True,
        verbose_name='Copia Carbónica Oculta'
    )

    @classmethod
    def create_for_event(cls, event):
        """
        Hard overwrite of django mailer's send_mail method generating relations
        between models
        """
        for email_assoc in event.di.email_associations.all():
            message = email_assoc.render_template(event=event)
            for user in email_assoc.targets.all():
                message = EmailNotificationAssociation.send_mail(
                    subject=email_assoc.subject,
                    message=message,
                    from_email=settings.SERVER_EMAIL,
                    recipient_list=[user.email]
                )
                MessageLogEventRelation.objects.create(event=event, message=message)



    @staticmethod
    def send_mail(subject, message, from_email, recipient_list,
                  priority="medium", fail_silently=False, auth_user=None, auth_password=None):
        from django.utils.encoding import force_unicode
        from mailer.models import Message
        from mailer import PRIORITY_MAPPING

        priority = PRIORITY_MAPPING[priority]

        # need to do this in case subject used lazy version of ugettext
        subject = force_unicode(subject)
        message = force_unicode(message)

        if len(subject) > 100:
            subject = u"%s..." % subject[:97]

        for to_address in recipient_list:
            message = Message(
                    to_address=to_address,
                    from_address=from_email,
                    subject=subject,
                    message_body=message,
                    priority=priority
            )
            message.save()
            return message

    class Meta:
        verbose_name = u"Regla de Envío de Correo electrónico"
        verbose_name_plural = u"Reglas de Envío de Correo electrónico"


class NotificationRequest(models.Model):
    """
    Notification request.
    Intitially for SMS, this will be generated with
    DIs with TAGs 52x, 51_ and 81
    """
    STATUS_CREATED = 'c'
    STATUS_PROCESSING = 'p'
    STATUS_ERROR = 'd'
    STATUS_SUCCESS = 's'

    STATUS_CHOICES = (
        (STATUS_CREATED, 'Pendiente', ),
        (STATUS_PROCESSING, 'En proceso', ),
        (STATUS_ERROR, 'Error', ),
        (STATUS_SUCCESS, 'Enviado', )
    )

    content_type = models.ForeignKey(
        ContentType,
        editable=False,
    )
    object_id = models.PositiveIntegerField(
        editable=False,
    )
    source = generic.GenericForeignKey(
        'content_type', 'object_id',
    )

    creation_time = models.DateTimeField(
        auto_now=True,
        verbose_name="Creación"
    )
    last_status_change_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=u"Última acutalización",
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name="Estado"
    )

    destination = models.CharField(
        max_length=100,
        verbose_name="Destinatario"
    )

    body = models.CharField(
        max_length=200,
        verbose_name="Cuerpo"
    )

    class Meta:
        verbose_name = "Encolamiento de SMS"
        verbose_name_plural = "Encolamientos de SMS"

    def __unicode__(self):
        return u'<Notificacion {} {}>'.format(self.destination, self.body[:20])


class MessageLogEventRelation(models.Model):
    """Relation between event and message log"""

    event = models.ForeignKey(
        Event,
        related_name='related_emails',
    )

    message = models.ForeignKey(
        Message,
        related_name='related_events',
    )

@receiver(signals.post_save, sender=Event, dispatch_uid="event.sms_and_email_notifications")
def create_request(instance, created, **kwargs):
    """Event hook on Event creation. Creates notification requests that later
    a management command will use to send notifications by SMS.
    """
    if created:
        print "FOOO", instance
        SMSNotificationAssociation.create_for_event(event=instance)
        EmailNotificationAssociation.create_for_event(event=instance)
