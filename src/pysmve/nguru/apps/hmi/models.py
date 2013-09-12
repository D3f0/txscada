# -*- coding: utf-8 -*-
import re
from bunch import bunchify
from datetime import datetime
from lxml.etree import ElementTree as ET
from django.db import models
from colorful.fields import RGBColorField

from apps.mara.models import Profile, AI, DI
# Formulas
from utils import generate_tag_context, IF, OR
# Internationalization
from django.utils.translation import ugettext_lazy as _
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
        verbose_name = _('SVG Screen')
        verbose_name_plural = _('SVG Screens')



def get_elements(et):
    tag = lambda t: re.sub('\{.*\}', '', t)
    return dict([(elem.attrib['tag'], tag(elem.tag)) for elem in et.findall('//*[@tag]')])


class Color(ProfileBound):
    name = models.CharField(max_length=30)
    color = RGBColorField()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name= _("Color")
        verbose_name_plural = _("Colors")



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
        verbose_name = _('SVG Property Change Set')
        verbose_name_plural = _('SVG Property Change Sets')



class SVGElement(models.Model):
    '''
    Alias of Elemento Grafico, EG.
    Represents a
    '''
    MARK_CHOICES = [ ("%s" % i, i) for i in xrange(16)]


    screen = models.ForeignKey(SVGScreen,
                               related_name='elements',
                               blank=True,
                               null=True)
    tag = models.CharField(max_length=16)
    description = models.CharField(max_length=120)
    # Attributes
    text = models.CharField(max_length=120, default='0')
    colbak = models.IntegerField(default=0)
    mark = models.IntegerField(null=True, blank=True, choices=MARK_CHOICES)
    enabled = models.BooleanField(default=False)
    # Used for checking when there are updates to send to clients
    last_update = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.tag

    _cached_colors = None
    @property
    def colors(self):
        if self._cached_colors is None:
            colors = {}
            fields = ('index', 'foreground__color', 'background__color')
            for index, fore, back in SVGPropertyChangeSet.objects.values_list(*fields):
                colors[index] = {'fill': back, 'color': fore}
            self._cached_colors = colors
        return self._cached_colors

    @property
    def style(self):
        '''Returns a dict of style/css properties for SVG'''
        try:
            return self.colors[self.colbak]
        except KeyError:
            return {}

    def svg_style(self):
        '''Return CSS style for SVG'''
        attrs = [ '%s: %s' % (k, str(v)) for k, v in self.style.iteritems()]
        return '%s' % '; '.join(attrs)

    class Meta:
        verbose_name = _("SVG Element")
        verbose_name_plural = _("SVG Elements")

class Formula(models.Model):

    ATTR_TEXT = 'text'
    ATTR_BACK = 'colbak'

    ATTRIBUTE_CHOICES = (
        (_('Text'), ATTR_TEXT),
        (_('Color/Background'), ATTR_BACK, ),
    )
    #tag = models.CharField(max_length=16)
    target = models.ForeignKey(SVGElement,
                               blank=True,
                               null=True,
                               verbose_name=_('target'))
    attribute = models.CharField(max_length=16,
                                 verbose_name=_('attribute'),
                                 choices=ATTRIBUTE_CHOICES
                                )
    formula = models.TextField()
    last_error = models.TextField()

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
    def calculate(cls, now=None):
        if not now:
            now = datetime.now()

        ai = generate_tag_context(AI.objects.values('tag', 'escala', 'value', 'q'))
        di = generate_tag_context(DI.objects.values('tag', 'value'))
        eg = generate_tag_context(SVGElement.objects.values('tag', 'text', 'colbak'))
        # Generate context for formula evaluation
        context = bunchify(dict(
                                # Datos
                                ai=ai,
                                di=di,
                                eg=eg,
                                # Funciones
                                RAIZ=lambda v: v ** .5,
                                SI=IF,si=IF,
                                O=OR,
                                )
                        )

        success, fail = 0, 0

        for formula in cls.objects.all():
            # Fila donde se guarda el cálculo
            element = formula.target
            texto_formula = formula.formula
            # Fix equal
            texto_formula = texto_formula.replace('=', '==')
            try:
                #import pdb; pdb.set_trace()
                value = eval(texto_formula, {}, context)
            except Exception as e:
                fail += 1
                # Record error
                formula.last_error = '%s: %s' % (type(e).__name__, e.message)
                formula.save()
            else:
                success += 1
                if formula.last_error:
                    formula.last_error = ''
                    formula.save()
                #print "Setenado", element.tag, formula.attribute, value
                attribute = formula.attribute
                prev_value = getattr(element, attribute)
                if prev_value != value:
                    # Update
                    setattr(element, attribute, value)
                    element.last_update = datetime.now()

                    element.save()

        # TODO: Check profile
        never_updated = SVGElement.objects.filter(last_update__isnull=True)
        never_updated.update(last_update=now)
        return success, fail

    @staticmethod
    def is_balanced(text):
        stack = []
        pushChars, popChars = "<({[", ">)}]"
        for c in text :
            if c in pushChars :
                stack.append(c)
            elif c in popChars :
                if not len(stack) :
                    return False
                else :
                    stackTop = stack.pop()
                    balancingBracket = pushChars[popChars.index(c)]
                    if stackTop != balancingBracket :
                        return False
            else:
                return False
        return not len(stack)

    class Meta:
        verbose_name = _("Formula")
        verbose_name_plural = _("Formulas")