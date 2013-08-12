# -*- coding: utf-8 -*-
import re
from bunch import bunchify
from datetime import datetime
from lxml.etree import ElementTree as ET
from colorful.fields import RGBColorField

from django.db import models
from apps.mara.models import AI, DI


class Screen(models.Model):
    parent = models.ForeignKey('self',
                               related_name='children',
                               null=True,
                               blank=True)

    class Meta:
        abstract = True


class SVGScreen(Screen):
    svg = models.FileField(upload_to="svg_screens")
    name = models.CharField(max_length=60)
    root = models.BooleanField(default=False)

    _svg = None
    _etree = None

    @property
    def etree(self):
        if not self._etree:
            self._etree = ET(file=self.svg.path)
        return self._etree

    @property
    def width(self):
        width = self.etree.getroot().attrib['width']
        return width.split('.')[0]

    @property
    def height(self):
        height = self.etree.getroot().attrib['height']
        return height.split('.')[0]

    _tags = None

    @property
    def tags(self):
        if self._tags is None:
            self._tags = get_elements(self.etree)
        return self._tags

    def __unicode__(self):
        return self.name


def get_elements(et):
    tag = lambda t: re.sub('\{.*\}', '', t)
    return dict([(elem.attrib['tag'], tag(elem.tag)) for elem in et.findall('//*[@tag]')])


class Color(models.Model):
    name = models.CharField(max_length=30)
    color = RGBColorField()

    def __unicode__(self):
        return self.name


class SVGPropertyChangeSet(models.Model):

    '''Formula evaluation result'''
    index = models.IntegerField()
    background = models.ForeignKey(Color,
                                   blank=True,
                                   null=True,
                                   related_name='backgrounds'
                                   )
    foreground = models.ForeignKey(Color,
                                   blank=True,
                                   null=True,
                                   related_name='foregrounds'
                                   )
    description = models.CharField(max_length=50,
                                   blank=True,
                                   null=True,
                                   )

    def __unicode__(self):
        return self.description


    class Meta:
        db_table = 'color'


class SVGElement(models.Model):
    MARK_CHOICES = [ ("%s" % i, i) for i in xrange(16)]
    tag = models.CharField(max_length=16)
    description = models.CharField(max_length=120)
    text = models.CharField(max_length=20, null=True, blank=True)
    background = models.CharField(max_length=20, null=True, blank=True)
    mark = models.IntegerField(null=True, blank=True, choices=MARK_CHOICES)
    enabled = models.BooleanField(default=False)
    last_update = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.tag

class Formula(models.Model):
    ATTR_TEXT = 'text'
    ATTR_BACK = 'colback'
    ATTR_FORE = 'colfore'
    ATTRIBUTE_CHOICES = (
        ('Text', ATTR_TEXT),
        ('Background', ATTR_BACK, ),
        ('Foreground', ATTR_FORE, ),
    )
    tag = models.CharField(max_length=16)
    attribute = models.CharField(max_length=16,)#hoices=ATTRIBUTE_CHOICES)
    formula = models.TextField()

    def __unicode__(self):
      return ":".join([self.tag, self.attribute])

    @classmethod
    def calculate(cls):
        def tag_dict(qs):
            result = {}
            for d in qs:
                key = d.pop('tag', None)
                if key:
                    result[key] = d
            return result
        ai = tag_dict(AI.objects.values('tag', 'escala', 'value'))
        di = tag_dict(DI.objects.values('tag', 'value'))
        eg = tag_dict(SVGElement.objects.values('tag', 'text'))

        def SI(cond, t, f):
            if cond:
                return t
            else:
                return f
        context = bunchify(dict(
                                # Datos
                                ai=ai,
                                di=di,
                                eg=eg,
                                # Funciones
                                RAIZ=lambda v: v ** .5,
                                SI=SI,
                                )
                        )
        for formula in cls.objects.all():
            # Fila donde se guarda el cálculo
            eg = SVGElement.objects.get(tag=formula.tag)
            texto_formula = formula.formula
            try:
                value = eval(texto_formula, {}, context)
            except Exception as e:
                print "Error parseando la formula: %s" % texto_formula
                print e
            else:
                #print "Setenado", eg.tag, formula.attribute, value
                attribute = formula.attribute
                prev_value = getattr(eg, attribute)
                if prev_value != value:
                    # Update
                    setattr(eg, attribute, value)
                    eg.last_update = datetime.now()
                    eg.save()
