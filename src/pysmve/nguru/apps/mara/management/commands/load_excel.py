import os
from collections import namedtuple, OrderedDict
from logging import getLogger
from optparse import make_option

from apps.hmi.models import (Color, Formula, SVGElement, SVGPropertyChangeSet,
                             SVGScreen)
from apps.mara.models import (Action, COMaster, ComEventKind, EventDescription,
                              EventText, Profile)
from apps.mara.utils import cd
from bunch import bunchify
from django.core.management.base import CommandError, NoArgsCommand
from django.utils.translation import ugettext_lazy as _

result_type = namedtuple('Result', 'ok error total')
#from apps.hmi.models import SVGElement


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


def import_profile_from_workbook(profile, workbook, svg_path,
                                 post_calculate=False,):
    """Command independent importer"""

    # Process COMaster for profile
    COMaster.import_excel(workbook, profile=profile)
    # Configuration for text representation of events
    EventText.import_excel(workbook, profile=profile)
    EventDescription.import_excel(workbook, profile=profile)
    ComEventKind.import_excel(workbook, profile=profile)
    Action.import_excel(workbook, profile=profile)

    # Fabric inspired directory change
    with cd(svg_path):
        SVGScreen.import_excel(workbook, profile=profile)

    SVGElement.import_excel(workbook, screens=profile.screens.all())
    Formula.import_excel(workbook, screens=profile.screens.all())
    Color.import_excel(workbook, profile=profile)
    SVGPropertyChangeSet.import_excel(workbook, profile=profile)

    if post_calculate:
        ok, error = Formula.calculate()
        return result_type(ok, error, ok + error)
    return result_type(0, 0, Formula.objects.all().count())


class Command(NoArgsCommand):
    option_list = (
        make_option('-e', '--excel', dest='workbook',
                    help="Archivo excel", default=None),
        make_option(
            '-p', '--profile', help='Profile donde cargar las formulas'),
        make_option(
            '-c', '--clear', help="Quitar valores previos", default=False,
            action='store_true', ),
        # make_option('-s', '--screen', help="Nombre de la pantalla en la que se quiere "
        #             "agregar las formulas", ),
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

    def handle_noargs(self, **options):
        self.options = bunchify(options)
        svg_path = self.options.svg_path
        if svg_path is None:
            svg_path = os.path.dirname(self.options.workbook)

        workbook = self.open_workbook()
        profile = Profile.get_profile(self.options.profile, self.options.clear)

        result = import_profile_from_workbook(profile, workbook,
                                              svg_path=svg_path,
                                              post_calculate=self.options.post_calculate)
        if result.error:
            logger.warning("Formulas con error: %2d" % result.error)
        logger.info("Formulas calculadas OK: %2d" % result.ok)
        logger.info("Total: %2d" % result.total)
