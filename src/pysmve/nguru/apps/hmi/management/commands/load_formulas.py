# -*- coding: utf-8 -*-
import os
from optparse import make_option
from collections import namedtuple, OrderedDict
import xlrd
from django.core.management.base import NoArgsCommand, CommandError

sanitize_row_name = lambda name: name.lower().replace(' ', '_')


def extract(row, fields=None):
    '''Extracts attribute from row'''
    if not fields:
        return row

    result = []
    for name in fields:
        result.append(getattr(row, name))
    return tuple(result)


class Command(NoArgsCommand):
    option_list = (
        make_option('-e', '--excel', dest='workbook',
                    help="Archivo excel", default=None),
        make_option(
            '-p', '--profile', help='Profile donde cargar las formulas'),
        make_option('-c', '--clear', help="Quitar formulas previas")
        #
    ) + NoArgsCommand.option_list

    def handle_noargs(self, **options):
        self.options = options

        self.load_formulas()

    def load_formulas(self):
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

        self.formulas_sheet = self.get_formulas_sheet()
        for tag, atributo, formula in self.iter_rows('tag', 'atributo', 'formula'):
            print tag, atributo, formula

    FORMULA_SHEET_NAME = 'formulas'

    def get_formulas_sheet(self):
        for sheet in self.workbook.sheets():
            sheet_name = sheet.name.lower()
            if sheet_name == self.FORMULA_SHEET_NAME:
                return sheet
        raise CommandError("No se pudo encontrar la hoja de formulas!")

    FIELD_LABELS_ROW = 0
    FIRST_DATA_ROW = 1

    def iter_rows(self, *extract_values):
        '''Iterates sheet returing named tuple for each row'''
        col_names = self.get_col_names()
        col_type = namedtuple('Row', col_names)
        print col_names
        for i in range(self.FIRST_DATA_ROW, self.formulas_sheet.nrows):
            values = self.formulas_sheet.row_values(i)
            yield extract(col_type._make(values), fields=extract_values)

    def get_col_names(self):
        '''Validates column names, takes care of repeated column names'''
        names = OrderedDict()
        for new_name in self.formulas_sheet.row_values(self.FIELD_LABELS_ROW):
            new_name = sanitize_row_name(new_name)
            if not new_name in names:
                names[new_name] = 0
            else:
                names[new_name] += 1
                extra_name = "%s_%d" % (new_name, names[new_name])
                names[extra_name] = 0

        return names.keys()
