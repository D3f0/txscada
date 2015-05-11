# -*- coding: utf-8 -*-
from django.db import models
from apps.mara.models import DI
from django.contrib.auth.models import User

try:
    from django.contrib.contenttypes.generic import GenericForeignKey
except ImportError:
    from django.contrib.contenttypes.fields import GenericForeignKey


class NotificationAssociation(models.Model):
    """Assocaites events to persons to be notified"""
    name = models.CharField(
        verbose_name="Nombre de Regla",
        max_length=100,
        unique=True,
    )

    source_di = models.ManyToManyField(DI, verbose_name=u"Fuentes de notificación")
    targets = models.ManyToManyField(
        User,
        verbose_name=u"Destinatarios",
        help_text="Solo se muestran los usuarios que tengan un nro. de celular cargado.")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"Regla de Envío de SMS"
        verbose_name_plural = u"Reglas de Envíos de SMS"


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
        ('Creada', STATUS_CREATED),
        ('En proceso', STATUS_PROCESSING),
        ('Error', STATUS_ERROR),
        ('Exitosa', STATUS_SUCCESS)
    )

    source = GenericForeignKey(
    )

    creation_time = models.DateTimeField(
        auto_now=True
    )
    last_status_change_time = models.DateTimeField(
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED
    )
    error = models.TextField()

    destination = models.CharField(max_length=100)
    body = models.CharField(max_length=200)
