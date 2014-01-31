# -*- coding: utf-8 -*-
import math
import os
import re
from datetime import datetime
from logging import getLogger

from apps.mara.models import AI, DI, Profile
from apps.mara.utils import ExcelImportMixin
from bunch import bunchify
from colorful.fields import RGBColorField
from django.core.files import File
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from apps.mara.utils import longest_prefix_match
from lxml.etree import ElementTree as ET
from django.core import validators
from utils import generate_tag_context, IF, OR, FILTRAR, FLOAT

# Formulas
# Internationalization

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


class SVGScreen(Screen, ExcelImportMixin):
    profile = models.ForeignKey(Profile, related_name='screens')
    svg = models.FileField(upload_to="svg_screens")
    name = models.CharField(max_length=60, verbose_name=_("Label"))
    prefix = models.CharField(max_length=4,
                              help_text=_("Related formula prefix"),
                              verbose_name=_("Prefix"))
    description = models.CharField(max_length=100, blank=True, null=True)

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


    @classmethod
    def do_import_excel(cls, workbook, models):
        """ Import SVG Screens from XLS sheet, it must be run in appropiate directory"""
        fields = ('path name  description prefix  parent'.split())
        inserted = {}
        for path, name, description, prefix, parent in\
            workbook.iter_as_dict('screens', fields=fields):
            if parent:
                if not parent in inserted:
                    raise ValueError("Screen %s is not previously defined" % parent)
                parent = inserted[parent]
            else:
                parent = None # Root screen
            screen = cls.objects.create(profile=models.profile,
                                        name=name,
                                        parent=parent,
                                        prefix=prefix)
            # http://stackoverflow.com/questions/1993939/programmatically-upload-files-in-django
            with open(path, 'rb') as fp:
                screen.svg.save(os.path.basename(path), File(fp), save=True)
            # Save File
            inserted[name] = screen
            screen.save()


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
            # print colour, cell.value
            rgb_color = '#%.2x%.2x%.2x' % colour
            models.profile.color_set.get_or_create(
                name=cell.value.title(),
                color=rgb_color
            )

    class Meta:
        verbose_name = _("Color")
        verbose_name_plural = _("Colors")


class SVGPropertyChangeSet(ProfileBound, ExcelImportMixin):

    '''Formula evaluation result'''
    index = models.IntegerField()

    color = models.ForeignKey(Color,
                              blank=True,
                              null=True,
                              related_name='colors'
                              )

    description = models.CharField(max_length=50,
                                   blank=True,
                                   null=True,
                                   )

    def __unicode__(self):
        return self.description

    @classmethod
    def do_import_excel(cls, workbook, models):
        fields = 'id_col color description'.split()
        for index, color, description in workbook.iter_as_dict('color', fields=fields):
            color_prop = None
            if color:
                color_prop = Color.objects.get(name__icontains=color)

            models.profile.svgpropertychangeset_set.create(
                index=index,
                color=color_prop,
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
    MARK_CHOICES = [(i, "%s" % i) for i in xrange(16)]

    screen = models.ForeignKey(SVGScreen,
                               related_name='elements',
                               blank=True,
                               null=True,
                               verbose_name=_('screen'))

    tag = models.CharField(max_length=16)

    description = models.CharField(max_length=120, verbose_name =_("description"))

    # Attributes
    text = models.CharField(max_length=120,
                            default='0',
                            blank=True,
                            verbose_name=_("text"))
    # Coloring
    fill = models.IntegerField(blank=True,
                               null=True,
                               verbose_name=_("fill"))

    stroke = models.IntegerField(blank=True,
                                 null=True,
                                 verbose_name=_("stroke"))

    mark = models.IntegerField(null=True,
                               blank=True,
                               choices=MARK_CHOICES)

    enabled = models.BooleanField(default=True,
                                  verbose_name=_("enabled"))
    # Used for checking when there are updates to send to clients
    last_update = models.DateTimeField(null=True,
                                       blank=True,
                                       editable=False,
                                       verbose_name=_('last update'))

    on_click_jump = models.ForeignKey(SVGScreen,
                                      blank=True,
                                      null=True,
                                      verbose_name=_("on click jump"),
                                      help_text=_("Screen destination when the object "
                                                  "is clicked")
                                      )

    TEXT_TOGGLE_REGEX = re.compile('''
        ^[\d\w]+
        \s?
        (\([\w\d\s]+\))?
        \,\s?
        [\d\w]+
        \s?
        (\([\w\d\s]+\))?
        $
    ''', flags= re.VERBOSE | re.UNICODE)

    on_click_text_toggle = models.CharField(max_length=50,
                                            blank=True, null=True,
                                            verbose_name=_('on click text toggle'),
                                            help_text=_("Text to toggle on click. "
                                                "Separated by coma (,)."),
                                            validators=[
                                            validators.RegexValidator(
                                                regex=TEXT_TOGGLE_REGEX,
                                                #message,
                                                #code
                                            )



                                            ])

    linked_text_change = models.CharField(max_length=120,
                                          blank=True,
                                          null=True,
                                          verbose_name=_('linked text change'),
                                          help_text=_('Text on related element will be '
                                                      'upon save')
                                          )
    @property
    def linked_text_change_dict(self):
        d = {}
        regex = re.compile('(?P<name>[\d\w]+)\s?(?P<description>\([\w\d\s]+\))?')
        if self.on_click_text_toggle:
            for option in self.on_click_text_toggle.split(','):
                match = regex.search(option)
                name = match.group('name')
                value = match.group('description')
                if value:
                    value = value.strip(')').strip('(')
                else:
                    value = name
                d[name] = value
        return d


    def __unicode__(self):
        return self.tag

    _cached_colors = None

    @classmethod
    def get_color_table(cls):
        if cls._cached_colors is None:
            fields = ('index', 'color__color')
            colors = dict(SVGPropertyChangeSet.objects.values_list(*fields))
            cls._cached_colors = colors
        return cls._cached_colors

    @property
    def style(self):
        '''Returns a dict of style/css properties for SVG'''
        retval = {}
        color_table = self.get_color_table()
        if self.fill:
            retval.update(fill=color_table[self.fill])
        if self.stroke:
            retval.update(stroke=color_table[self.stroke])
        return retval

    def svg_style(self):
        '''Return CSS style for SVG'''
        attrs = ['%s: %s' % (k, str(v)) for k, v in self.style.iteritems()]
        return '%s' % '; '.join(attrs)

    @property
    def formulas(self):
        d = {}
        for formula in self.formula_set.all():
            d.update({formula.attribute: formula.formula})
        return d


    @classmethod
    def do_import_excel(cls, workbook, models):
        """Import form excel file, sheet 'eg'"""
        fields = ('tag', 'description', 'text', 'fill', 'stroke', 'mark')
        created_tags = set()
        screen_prefix_map = dict([(m.prefix, m) for m in\
                                    models.screens.only('pk', 'prefix')])

        for tag, description, text, fill, stroke, mark in\
                workbook.iter_as_dict('eg', fields=fields):
            # Prevent tag from repeating
            i = 0
            base_tag = tag
            while base_tag in created_tags:
                cls.get_logger().warning(unicode(_("Tag repeated %s" % base_tag)))
                base_tag = '%s_%d' % (base_tag, i)
                i += 1
            tag = base_tag
            if type(text) is float:
                frac, val = math.modf(text)
                if not frac:
                    text = str(int(val))
            screen = longest_prefix_match(tag, screen_prefix_map)

            screen.elements.create(
                tag=tag,
                description=description,
                text=text,
                fill=fill or None,
                stroke=stroke or None,
                mark=mark or None,
            )
            created_tags.add(tag)

    class Meta:
        verbose_name = _("SVG Element")
        verbose_name_plural = _("SVG Elements")

    @classmethod
    def update_modification_timestamp(cls, instance=None, **kwargs):
        instance.last_update = datetime.now()

    @classmethod
    def update_linked_text_change(cls, instance=None, **kwargs):
        """Update text in related tag. It uses update so no reucrssion limit problem is
        arraised"""
        if not instance.linked_text_change:
            return
        rel_tags = instance.linked_text_change.split(',')

        for rel_tag in rel_tags:
            instance.screen.elements.filter(tag=rel_tag).update(text=instance.text)

signals.pre_save.connect(SVGElement.update_modification_timestamp,
                         sender=SVGElement)

signals.post_save.connect(SVGElement.update_linked_text_change,
                         sender=SVGElement)

class Formula(models.Model, ExcelImportMixin):

    ATTRIBUTE_CHOICES = (
        ('fill', _('fill')),
        ('stroke', _('stroke')),
        ('text', _('text')),
    )
    target = models.ForeignKey(SVGElement,
                               blank=True,
                               null=True,
                               verbose_name=_('target'))
    attribute = models.CharField(max_length=16,
                                 verbose_name=_('attribute'),
                                 choices=ATTRIBUTE_CHOICES
                                 )
    formula = models.TextField()
    last_error = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return ":".join([self.target.tag, self.attribute])

    @classmethod
    def link_with_svg_element(cls, profile_name='default'):
        svg_elements_qs = SVGElement.objects.all()  # TODO: Filter
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
    def calculate(cls, comaster_pk=None, now=None):
        '''
        Calculates and updates EGs based on the formula table.
        '''
        if not now:
            now = datetime.now()

        filters = dict(ied__co_master__pk=comaster_pk)
        filters = {}

        ai = generate_tag_context(AI.objects.filter(**filters).values(
                                  'tag', 'escala', 'value', 'q')
                                  )
        di = generate_tag_context(DI.objects.filter(**filters).values('tag', 'value')
                                  )
        eg = generate_tag_context(
            SVGElement.objects.values('tag', 'text', 'fill', 'stroke', 'mark'))
        # Generate context for formula evaluation
        context = bunchify(dict(
            # Datos
            ai=ai,
            di=di,
            eg=eg,
            # Funciones
            RAIZ=lambda v: v ** .5,
            SI=IF, si=IF,
            O=OR,
            SUMA=sum,
            APLICAR=map,
            FILTRAR=FILTRAR,
            FLOAT=FLOAT
            )
        )

        success, fail = 0, 0

        for formula in cls.objects.all():
            # Fila donde se guarda el cálculo
            element = formula.target
            texto_formula = formula.formula
            # Fix single equal sign
            #texto_formula = re.sub(r'(?:[\b\s])=(:?[\s\b])', '==', texto_formula)
            texto_formula = texto_formula.replace('=', '==')
            try:
                #import pdb; pdb.set_trace()
                value = eval(texto_formula, {}, context)
            except Exception as e:
                fail += 1
                # Record error
                formula.last_error = '%s: %s' % (type(e).__name__, e.message)
                print e, formula.target.tag, formula.attribute, texto_formula
                import traceback; traceback.print_exc();
                formula.save()
            else:
                success += 1
                if formula.last_error:
                    formula.last_error = ''
                    formula.save()
                # print "Setenado", element.tag, formula.attribute, value
                attribute = formula.attribute
                prev_value = getattr(element, attribute)
                if prev_value != value:
                    # Update
                    setattr(element, attribute, value)
                    element.save()

        # TODO: Check profile
        never_updated = SVGElement.objects.filter(last_update__isnull=True)
        never_updated.update(last_update=now)
        return success, fail

    @staticmethod
    def is_balanced(text):
        stack = []
        pushChars, popChars = "<({[", ">)}]"
        for c in text:
            if c in pushChars:
                stack.append(c)
            elif c in popChars:
                if not len(stack):
                    return False
                else:
                    stackTop = stack.pop()
                    balancingBracket = pushChars[popChars.index(c)]
                    if stackTop != balancingBracket:
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
                                                                   fields=fields):
            if not formula or not atributo:
                continue
            try:
                target= SVGElement.objects.get(tag=tag, screen__in = models.screens)
            except SVGElement.DoesNotExist:
                print("Skipping %s %s" % (tag, formula))

            Formula.objects.create(
                target=target,
                formula=formula,
                attribute=attr_trans.get(atributo, atributo)
            )

    class Meta:
        verbose_name = _("Formula")
        verbose_name_plural = _("Formulas")
