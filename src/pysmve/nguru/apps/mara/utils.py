# encoding: utf-8
from __future__ import print_function

import os
from collections import namedtuple, OrderedDict
from contextlib import contextmanager
from logging import getLogger
from functools import wraps, partial
import itertools
import xlrd
from bunch import bunchify
import glob
import re
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
        logger = cls.get_logger()
        retval = cls.do_import_excel(workbook, bunchify(models), logger=logger)
        logger.info("Importing %s" % unicode(cls._meta.verbose_name))
        return retval

    @classmethod
    def do_import_excel(cls, workbook, models, logger):
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


# Taken from ()
class Indexable(object):
    def __init__(self, it):
        self.it = it
        self.already_computed = []

    def __iter__(self):
        for elt in self.it:
            self.already_computed.append(elt)
            yield elt

    def __getitem__(self, index):
        try:
            max_idx = index.stop
        except AttributeError:
            max_idx = index
        n = max_idx-len(self.already_computed)+1
        if n > 0:
            self.already_computed.extend(itertools.islice(self.it, n))
        return self.already_computed[index]


def counted(fn):
    """Count invocations to method/function"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        wrapper.called += 1
        return fn(*args, **kwargs)
    wrapper.called = 0
    return wrapper

mara_frame_regex = re.compile(r'(FE ([0-9A-F]{2}\s?){2,512})', re.IGNORECASE)


def get_ascii_from_logs(logdir, count=0, frame_count=0, older_first=False):
    """Parses logs in directory and find mara frames
    They are not parsed through a specific comaster (not saved to DB).
    `logdir` can be a glob experssion.
    `count` indicates how many files should be parsed (if 0 no limit).
    `frame_count` indicates how many frames (if 0 no limit).
    """
    if os.path.isdir(logdir):
        logdir = os.path.join(logdir, '*.*')
    # Apply sorting
    files = glob.glob(logdir)
    files.sort(key=lambda f: os.stat(f).st_mtime, reverse=not older_first)
    # Iterate thourgh files
    frames = 0
    for numfile, f in enumerate(files):
        if count and numfile > count:
            break
        with open(f) as fp:
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                match = mara_frame_regex.search(line)
                if match:
                    yield match.group()
                    frames += 1
                    if frame_count and frames > frame_count:
                        break


def build_filter_funcs(func_or_list):
    '''Converts multiple filter functions in a single function.
    It accepts None, a callable or a list of callables and returns a function.
    If func_or_list is None, a function returning always True is returned.
    If func_or_list is a function, that function is returned.
    If func_or_list is a list of functions, a function '''
    if not func_or_list:
        return lambda v: True
    elif callable(func_or_list):
        return func_or_list
    elif isinstance(func_or_list, (tuple, list)):
        return lambda v: all(itertools.imap(lambda f: f(v), func_or_list))


def get_structs_from_logs(logdir, count=0, frame_count=0, older_first=False,
                          filter_func=None):
    """Uses get_ascii_from_logs to get ascii frames and then it parses them
    using construct.
    Notice that parsing may fail and/or """
    from protocols.constructs import MaraFrame
    from protocols.constructs.structs import hexstr2buffer
    from construct import FieldError
    count = 0
    filters = build_filter_funcs(filter_func)
    for ascii_frame in get_ascii_from_logs(logdir,
                                           count=count,
                                           frame_count=0,  # Cutting at upper level
                                           older_first=older_first):
        buffer = hexstr2buffer(ascii_frame)
        try:
            container = MaraFrame.parse(buffer)
        except (ValueError, FieldError):
            continue
        if not filters(container):
            continue

        yield container
        count += 1
        if frame_count and count > frame_count:
            break


def filter_cmd_10_resp(container):
    cmd = container.get('command')
    payload = container.get('payload_10')
    return cmd == 0x10 and payload is not None

get_0x10_resp_from_logs = partial(get_structs_from_logs, filter_func=filter_cmd_10_resp)


def get_energy_23_59_from_logs(*args, **kwargs):
    '''Same as get structs but filters those events which are ENERGY and at 23:59'''
    def f_filter(container):
        try:
            for ev in container.payload_10.event:
                if ev.evtype == "ENERGY" and ev.hour == 23 and ev.minute == 59:
                    return True
        except AttributeError:
            pass
        return False
    return Indexable((container for container in get_structs_from_logs(*args, **kwargs)
                     if f_filter(container)))

