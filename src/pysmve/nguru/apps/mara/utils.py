from __future__ import print_function
import xlrd
from collections import OrderedDict, namedtuple
from bunch import bunchify
from django.utils.translation import ugettext_lazy as _
from logging import getLogger

try:
    from fabric.colors import red, green, blue, yellow
except ImportError:
    null_color = lambda t, b=False: t
    red = green = blue = yellow = null_color

def sanitize_row_name(name):
    name = name.lower().replace(' ', '_').replace('-', '_')
    if not name:
        name = 'no_now_name'
    elif name.startswith('_'):
        name = 'column_%s' % name
    return name

def extract(row, fields=None):
    '''Extracts attribute from row'''
    if not fields:
        result = row
    else:
        result = []
        for name in fields:
            try:
                result.append(getattr(row, name))
            except AttributeError:
                raise AttributeError("%s not in %s" % (name, row._fields))
    #result = map(lambda v: v if v is not '' else None, result)
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


class WorkBook(object):

    '''XLRD wrapper for easy access to excel data as dicts'''

    def __init__(self, filepath, **kwargs):
        self.book = xlrd.open_workbook(filepath, **kwargs)

    def iter_as_dict(self, sheet_name, fields=None, row_filter=None):
        sheet = self.book.sheet_by_name(sheet_name)
        for row in iter_rows(sheet, fields=fields):
            if callable(row_filter) and not row_filter(row):
                continue
            yield row

    def __getattr__(self, name):
        return getattr(self.book, name)

class ExcelImportMixin(object):
    '''Mixin for Django models'''

    _logger = None
    @classmethod
    def get_logger(cls):
        if cls._logger is None:
            cls._logger = getLogger('excel_import')
        return cls._logger

    @classmethod
    def import_excel(cls, workbook, **models):
        '''Import from excel'''
        try:
            retval = cls.do_import_excel(workbook, bunchify(models))
            cls.get_logger().info("Importing %s" % cls._meta.verbose_name)
        except Exception, e:
            raise e

        return retval

    @classmethod
    def do_import_excel(cls, workbook, models):
        raise NotImplementedError("Not implemented for %s" % cls)
