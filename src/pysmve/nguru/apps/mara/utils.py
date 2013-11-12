# encoding: utf-8
from __future__ import print_function

import os
from collections import namedtuple, OrderedDict
from contextlib import contextmanager
from logging import getLogger
from functools import wraps
import xlrd
from bunch import bunchify

try:
    from fabric.colors import red, green, blue, yellow
except ImportError:
    null_color = lambda t, b = False: t
    red = green = blue = yellow = null_color


def sanitize_row_name(name):
    name = name.lower().replace(' ', '_').replace('-', '_')
    if not name:
        name = 'no_now_name'
    elif name.startswith('_'):
        name = 'column_%s' % name
    return name



_row_type_registry = {}

def get_nametuple(fields):
    fields = tuple(fields)
    if not fields in _row_type_registry:
        _row_type_registry[fields] = namedtuple('Row', fields)
    return _row_type_registry[fields]



def extract(row, fields=None):
    '''Extracts attribute from row'''
    if not fields:
        result = row
    else:
        tmp_result = []
        for name in fields:
            try:
                tmp_result.append(getattr(row, name))
            except AttributeError:
                raise AttributeError("%s not in %s" % (name, row._fields))
        nt_type = get_nametuple(fields)
        result = nt_type._make(tmp_result)
    return result

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
        retval = cls.do_import_excel(workbook, bunchify(models))
        cls.get_logger().info("Importing %s" % unicode(cls._meta.verbose_name))

        return retval

    @classmethod
    def do_import_excel(cls, workbook, models):
        raise NotImplementedError("Not implemented for %s" % cls)


def get_relation_managers(model):
    for related in model._meta.get_all_related_objects():
        yield getattr(model, related.get_accessor_name())


@contextmanager
def cd(path):
    curr_path = os.getcwd()
    try:
        os.chdir(path)
        yield
    except Exception as e:
        os.chdir(curr_path)
        raise e


def longest_prefix_match(search, a_dict):
    matches = [prefix for prefix in a_dict if search.startswith(prefix)]
    if matches:
        return a_dict[max(matches, key=len)]

def counted(fn):
    """Count invocations to method/function"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        wrapper.called += 1
        return fn(*args, **kwargs)
    wrapper.called = 0
    return wrapper
