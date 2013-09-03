# -*- coding: utf-8 -*-
import re
from bunch import bunchify
from datetime import datetime
from lxml.etree import ElementTree as ET
from colorful.fields import RGBColorField

from django.db import models
from apps.mara.models import Profile, AI, DI

from logging import getLogger

logger = getLogger(__name__)

class ProfileBound(models.Model):
    profile = models.ForeignKey(Profile)

    class Meta:
        abstract = True

class Screen(models.Model):
    parent = models.ForeignKey('self',
                               related_name='children',
                               null=True,
                               blank=True)

    class Meta:
        abstract = True


class SVGScreen(Screen):
    profile = models.ForeignKey(Profile, related_name='screens')
    svg = models.FileField(upload_to="svg_screens")
    name = models.CharField(max_length=60)
    root = models.BooleanField(default=False)
    prefix = models.CharField(max_length=4, help_text="Related formula prefix")

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

    def prefix_formula_bind(self):
        assert len(self.prefix) > 1, "Prefix too short"
        qs = Formula.objects.filter(tag__starts_with=self.prefix)
        qs.update(screen=self)
        return qs


    class Meta:
        unique_together = ('prefix', 'profile')


def get_elements(et):
    tag = lambda t: re.sub('\{.*\}', '', t)
    return dict([(elem.attrib['tag'], tag(elem.tag)) for elem in et.findall('//*[@tag]')])


class Color(ProfileBound):
    name = models.CharField(max_length=30)
    color = RGBColorField()

    def __unicode__(self):
        return self.name


class SVGPropertyChangeSet(ProfileBound):
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

def closest_key(a_string, a_dict):
    '''Returns the closest key in a dictionary to a_string.
    The match is from the begining of the string and scores how
    may chars are the same
    '''
    keys = a_dict.keys()
    closest_key = None
    closest_score = 0

    for key in keys:
        score = 0
        for k_s, k_c in zip(a_string, key):
            if k_s != k_c:
                break
            score += 1
        if score >= closest_score:
            closest_score = score
            closest_key = key
    return closest_key


class SVGElement(ProfileBound):
    '''
    Alias of Elemento Grafico, EG.
    Represents a
    '''
    MARK_CHOICES = [ ("%s" % i, i) for i in xrange(16)]


    screen = models.ForeignKey(SVGScreen, blank=True, null=True)
    tag = models.CharField(max_length=16)
    description = models.CharField(max_length=120)
    # Attributes
    text = models.CharField(max_length=20, null=True, blank=True)
    background = models.CharField(max_length=20, null=True, blank=True)
    mark = models.IntegerField(null=True, blank=True, choices=MARK_CHOICES)
    enabled = models.BooleanField(default=False)
    # Used for checking when there are updates to send to clients
    last_update = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.tag

    @classmethod
    def link_with_screen(cls):
        svg_elements = SVGElement.objects.all()
        svg_screens = SVGScreen.objects.all()
        screen_prefix = dict(( (s.prefix, s) for s in svg_screens))
        for element in svg_elements:
            closest_key(element.tag, )



class Formula(models.Model):
    ATTR_TEXT = 'text'
    ATTR_BACK = 'colback'
    ATTR_FORE = 'colfore'
    ATTRIBUTE_CHOICES = (
        ('Text', ATTR_TEXT),
        ('Background', ATTR_BACK, ),
        ('Foreground', ATTR_FORE, ),
    )
    target = models.ForeignKey(SVGElement, blank=True, null=True)
    #tag = models.CharField(max_length=16)
    attribute = models.CharField(max_length=16,)#hoices=ATTRIBUTE_CHOICES)
    formula = models.TextField()

    def __unicode__(self):
      return ":".join([self.target.tag, self.attribute])

    @classmethod
    def link_with_svg_element(cls, profile_name='default'):
        svg_elements_qs = SVGElement.objects.all() # TODO: Filter
        for n, formula in enumerate(Formula.objects.all()):
            try:
                element = svg_elements_qs.get(tag=formula.tag)
            except SVGElement.MultipleObjectsReturned:
                repeated = svg_elements_qs.filter(tag=formula.tag)[1:].values('pk')
                svg_elements_qs.filter(pk__in=repeated).delete()
                element = svg_elements_qs.get(tag=formula.tag)
            formula.target = element
            formula.save()



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
