import os
from collections import namedtuple, OrderedDict
from django.core.management.base import NoArgsCommand, CommandError
from apps.mara.models import (Profile, COMaster, EventText, ComEventKind,
                              EventDescription, Action, )
from apps.hmi.models import SVGScreen, SVGElement, Formula, Color, SVGPropertyChangeSet
#from apps.hmi.models import SVGElement
from optparse import make_option
from django.utils.translation import ugettext_lazy as _
from bunch import bunchify
from django.core.files import File

from logging import getLogger

logger = getLogger('excel_import')

sanitize_row_name = lambda name: name.lower().replace(' ', '_')


def extract(row, fields=None):
    '''Extracts attribute from row'''
    if not fields:
        return row

    result = []
    for name in fields:
        result.append(getattr(row, name))
    return tuple(result)

FIELD_LABELS_ROW = 0
FIRST_DATA_ROW = 1


def iter_rows(sheet, fields=None, first_data_row=FIRST_DATA_ROW):
    '''Iterates sheet returing named tuple for each row'''
    col_names = get_col_names(sheet)
    col_type = namedtuple('Row', col_names)
    # print col_names
    for i in range(first_data_row, sheet.nrows):
        values = sheet.row_values(i)
        yield extract(col_type._make(values), fields=fields)


def get_col_names(sheet, field_labels_row=FIELD_LABELS_ROW):
    '''Validates column names, takes care of repeated column names'''
    names = OrderedDict()
    for new_name in sheet.row_values(field_labels_row):
        new_name = sanitize_row_name(new_name)
        if not new_name in names:
            names[new_name] = 0
        else:
            names[new_name] += 1
            extra_name = "%s_%d" % (new_name, names[new_name])
            names[extra_name] = 0

    return names.keys()


def get_relation_managers(model):
    for related in model._meta.get_all_related_objects():
        yield getattr(model, related.get_accessor_name())


class Command(NoArgsCommand):
    option_list = (
        make_option('-e', '--excel', dest='workbook',
                    help="Archivo excel", default=None),
        make_option(
            '-p', '--profile', help='Profile donde cargar las formulas'),
        make_option(
            '-c', '--clear', help="Quitar valores previos", default=False,
            action='store_true', ),
        make_option('-s', '--screen', help="Nombre de la pantalla en la que se quiere "
                    "agregar las formulas", ),
        make_option(
            '-C', '--post-calculate', default=False, action='store_true',
            help="Post calucla la formulas para ver los errores"),
        make_option(
            '-S', '--svg-path', help='Ruta al archivo SVG para la pantallla',
            dest='svg_path', default=None),

    ) + NoArgsCommand.option_list

    def open_workbook(self):
        from apps.mara.utils import WorkBook
        try:
            return WorkBook(self.options.workbook, formatting_info=True)
        except IOError:
            raise CommandError(
                _("File %s could not be read or it's not an excel file") %
                self.options.workbook)

    def get_profile(self):
        try:
            profile, created = Profile.objects.get_or_create(
                name=self.options.profile)
        except Exception, e:
            raise e

        if not created and self.options.clear:
            for manager in get_relation_managers(profile):
                count = manager.all().count()
                logger.warning(_("Clearing {0} {1}").format(
                                                    count,
                                                    manager.model._meta.verbose_name)
                )
                manager.all().delete()
        return profile

    def handle_noargs(self, **options):
        self.options = bunchify(options)
        if self.options.svg_path is not None:
            if not os.path.isfile(self.options.svg_path):
                raise CommandError(
                    _("Could not find SVG file %s") % self.options.svg_path)

        self.workbook = self.open_workbook()
        profile = self.get_profile()
        # Process COMaster for profile
        COMaster.import_excel(self.workbook, profile=profile)
        # Configuration for text representation of events
        EventText.import_excel(self.workbook, profile=profile)
        EventDescription.import_excel(self.workbook, profile=profile)
        ComEventKind.import_excel(self.workbook, profile=profile)
        Action.import_excel(self.workbook, profile=profile)
        screen = SVGScreen.objects.create(profile=profile,
                                          name=self.options.screen,
                                          root=False,
                                          prefix=self.options.screen[:2])
        # Save File
        screen.svg.save(os.path.basename(self.options.svg_path),
                        File(open(self.options.svg_path)))
        screen.save()
        SVGElement.import_excel(self.workbook, screen=screen)
        Formula.import_excel(self.workbook, screen=screen)
        Color.import_excel(self.workbook, profile=profile)
        SVGPropertyChangeSet.import_excel(self.workbook, profile=profile)