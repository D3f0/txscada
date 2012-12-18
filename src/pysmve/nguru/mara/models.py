# encoding: utf-8

from django.db import models
from protocols import constants

# Create your models here.
class Profile(models.Model):
    # Name of the 
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    # Version, something relevant for the user
    version = models.CharField(default='1', max_length=1)
    # Date of creation
    date = models.DateField(auto_now=True)


    class Meta:
        unique_together = ('name',)


class COMaster(models.Model):
    '''

    '''
    profile = models.ForeignKey(Profile)
    ip_address = models.IPAddressField()
    enabled = models.BooleanField(default=False)
    port = models.IntegerField(verbose_name="Puerto TCP de conexion",
                               default=constants.DEFAULT_COMASTER_PORT)
    poll_interval = models.FloatField(verbose_name="Intervalo de consulta en segundos",
                                      default=5)
    sequence = models.IntegerField(help_text=u"Número de secuencia")
    rs485_source = models.SmallIntegerField(default=0)
    rs485_destination = models.SmallIntegerField(default=0)

    def __unicode__(self):
        return u"%s" % self.ip_address


