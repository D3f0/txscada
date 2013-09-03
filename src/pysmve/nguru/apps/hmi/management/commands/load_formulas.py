# -*- coding: utf-8 -*-
import os
from optparse import make_option
from collections import namedtuple, OrderedDict
import xlrd
from django.core.management.base import NoArgsCommand, CommandError
from apps.hmi.models import Formula
from apps.mara.models import Profile


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
    #print col_names
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

class Command(NoArgsCommand):
    option_list = (
        make_option('-e', '--excel', dest='workbook',
                    help="Archivo excel", default=None),
        make_option(
            '-p', '--profile', help='Profile donde cargar las formulas'),
        make_option('-c', '--clear', help="Quitar formulas previas", default=False,
            action='store_true', ),
        make_option('-s', '--screen', help="Pantalla en la que se quiere agregar las "
            "formulas", )
    ) + NoArgsCommand.option_list

    def handle_noargs(self, **options):
        self.options = options

        self.load_formulas()

    def load_formulas(self):
        '''Load formulas from excel'''
        workbook_path = self.options.get('workbook')
        if not workbook_path:
            raise CommandError(
                "Debe especificar un nombre de archivo válido (-e/--excel)")
        elif not os.path.isfile(workbook_path):
            raise CommandError("%s no es un archivo valido" % workbook_path)
        try:
            self.workbook = xlrd.open_workbook(workbook_path)
        except IOError:
            raise CommandError("Error de entrada salida abriendo excel")

        formulas_sheet = self.get_formulas_sheet()

        try:
            name = self.options['profile']
            profile = Profile.objects.get(name=name)
        except Profile.DoesNotExist:
            raise CommandError("Profile %s does not exist" % name)

        deleted_count = 0
        created_count = 0

        if self.options['clear']:
            qs = profile.formula_set.all()
            deleted_count = qs.count()
            qs.delete()

        translation = {
            'text': Formula.ATTR_TEXT,
            'colbak': Formula.ATTR_BACK,
            'value': Formula.ATTR_TEXT,
        }
        fields = ('tag', 'atributo', 'formula')


        for tag, atributo, formula in iter_rows(formulas_sheet, fields):
            if not formula or not atributo:
                continue
            profile.formula_set.create(
                    tag=tag,
                    attribute=translation[atributo],
                    formula=formula
                )
            created_count += 1
        self.debug('Se crearon %d formulas' % created_count)
        self.debug('Se eliminaron %d formulas (por opción -c/--clear)' % deleted_count)

    def debug(self, msg, verbosity_thereshold=0):
        if self.options['verbosity'] > verbosity_thereshold:
            print(msg)

    FORMULA_SHEET_NAME = 'formulas'

    def get_formulas_sheet(self):
        for sheet in self.workbook.sheets():
            sheet_name = sheet.name.lower()
            if sheet_name == self.FORMULA_SHEET_NAME:
                return sheet
        raise CommandError("No se pudo encontrar la hoja de formulas!")


