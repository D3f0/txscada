# -*- coding: utf-8 -*-
import re
from bunch import bunchify
from datetime import datetime
from lxml.etree import ElementTree as ET
from django.db import models
from colorful.fields import RGBColorField

from apps.mara.models import Profile, AI, DI
from apps.mara.utils import ExcelImportMixin
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


class Color(ProfileBound, ExcelImportMixin):
    name = models.CharField(max_length=30)
    color = RGBColorField()

    def __unicode__(self):
        return self.name

    @classmethod
    def do_import_excel(cls, workbook, models):
        colour_map = workbook.colour_map
        sheet = workbook.sheet_by_name('color')
        rows, cols = sheet.nrows, sheet.ncols
        for row in range(1, rows):
            col = 2
            cell = sheet.cell(row, col)
            fmt = workbook.xf_list[cell.xf_index]
            colour = colour_map[fmt.background.pattern_colour_index]
            #print colour, cell.value
            rgb_color = '#%.2x%.2x%.2x' % colour
            models.profile.color_set.get_or_create(
                name = cell.value.title(),
                color=rgb_color
                )


    class Meta:
        verbose_name= _("Color")
        verbose_name_plural = _("Colors")



class SVGPropertyChangeSet(ProfileBound, ExcelImportMixin):
    '''Formula evaluation result'''
    index = models.IntegerField()
    fill_back = models.ForeignKey(Color,
                                   blank=True,
                                   null=True,
                                   related_name='backgrounds'
                                   )
    fill_fore = models.ForeignKey(Color,
                                   blank=True,
                                   null=True,
                                   related_name='foregrounds'
                                   )
    stroke = models.ForeignKey(Color,
                               blank=True,
                               null=True,
                               related_name='strokes'
                               )
    description = models.CharField(max_length=50,
                                   blank=True,
                                   null=True,
                                   )

    def __unicode__(self):
        return self.description

    @classmethod
    def do_import_excel(cls, workbook, models):
        fields = ('id_col', 'fill_bak', 'fill_for', 'stroke', 'description')
        for index, fill_back, fill_fore, stroke, description\
                in workbook.iter_as_dict('color', fields=fields):
            color_fill_back = color_fill_fore = color_stroke = None
            if fill_back:
                color_fill_back = Color.objects.get(name__icontains=fill_back)
            if fill_fore:
                color_fill_fore = Color.objects.get(name__icontains=fill_fore)
            if stroke:
                color_stroke = Color.objects.get(name__icontains=stroke)
            models.profile.svgpropertychangeset_set.create(
                index=index,
                fill_back=color_fill_back,
                fill_fore=color_fill_fore,
                stroke=color_stroke,
                description=description
            )

    class Meta:
        db_table = 'color'
        ordering = ('-index', )
        verbose_name = _('SVG Property Change Set')
        verbose_name_plural = _('SVG Property Change Sets')



class SVGElement(models.Model, ExcelImportMixin):
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
    # Coloring
    fill_back = models.IntegerField(blank=True,
                                    null=True)
    fill_fore = models.IntegerField(blank=True,
                                    null=True)
    stroke = models.IntegerField(blank=True,
                                 null=True)

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


    @classmethod
    def do_import_excel(cls, workbook, models):
        """Import form excel file, sheet 'eg'"""
        fields = ('tag', 'description', 'text', 'fill_for', 'fill_bak', 'stroke', 'mark')
        created_tags = set()
        for tag, description, text, fill_fore, fill_back, stroke, mark in\
                workbook.iter_as_dict('eg',fields=fields):
            # Prevent tag from repeating
            i = 0
            base_tag = tag
            while base_tag in created_tags:
                cls.get_logger().warning(unicode(_("Tag repeated %s" % base_tag)))
                base_tag = '%s_%d' % (base_tag, i)
                i += 1
            tag = base_tag
            models.screen.elements.create(
                tag=tag,
                description=description,
                text=text,
                fill_back=fill_back or None,
                fill_fore=fill_fore or None,
                stroke=stroke or None,
                mark=mark or None,
            )
            created_tags.add(tag)

    class Meta:
        verbose_name = _("SVG Element")
        verbose_name_plural = _("SVG Elements")

class Formula(models.Model, ExcelImportMixin):

    #tag = models.CharField(max_length=16)
    target = models.ForeignKey(SVGElement,
                               blank=True,
                               null=True,
                               verbose_name=_('target'))
    attribute = models.CharField(max_length=16,
                                 verbose_name=_('attribute'),
                                 #choices=ATTRIBUTE_CHOICES
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

    @classmethod
    def do_import_excel(cls, workbook, models):
        """Import form excel file, sheet 'formulas'"""
        attr_trans = {}
        fields = ('tabla', 'tag', 'atributo', 'formula')
        for tabla, tag, atributo, formula in workbook.iter_as_dict('formulas',
                                                                          fields=fields ):
            if not formula or not atributo:
                continue

            target, created = models.screen.elements.get_or_create(tag=tag)
            Formula.objects.create(
                target=target,
                formula=formula,
                attribute=attr_trans.get(atributo, atributo)
            )

    class Meta:
        verbose_name = _("Formula")
        verbose_name_plural = _("Formulas")