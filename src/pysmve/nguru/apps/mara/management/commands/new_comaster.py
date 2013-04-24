
from django.core.management.base import NoArgsCommand, CommandError
from apps.mara.models import Profile, IED, SV, DI, AI
from apps.hmi.models import SVGElement, Formula
from optparse import make_option
import os
from os.path import join, abspath, dirname, splitext, basename
from glob import glob
from bunch import Bunch
from codecs import open
from itertools import groupby
import re
import xlrd

PATH_TEMPLATES = join(dirname(abspath(__file__)), 'templates')

INVALID_KEYS = ('id', )


def try_int(v):
    try:
        return int(v)
    except ValueError:
        if re.match('\d+\,\d+', v):
            try:
                return float('.'.join(v.split(',')))
            except ValueError:
                pass
    return v.decode('latin1').encode('utf8')


def filter_dict_fields(model_class, args):
    data = {}
    fields = map(lambda f: f.name, model_class._meta.fields)
    for name, value in args.iteritems():
        name = name.lower()
        if name in fields:
            data[name] = value
    return data


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('-p', '--profile', help="Profile name",
                    dest='profile_name', default='default'),
        make_option('-a', '--address', help="IP address",
                    action='append', default=[], dest='co_ips'),
        make_option('-d', '--delete', help="Delete previous data",
                    action='store_true', default=False),

        make_option('-e', '--excel', help="Excel template",
                    default=None, ),
    )
    help = '''Crea un COMaster con sus IED asociados en un perfil dado'''

    def _read_templates(self):
        template = Bunch()
        for fname in glob(join(PATH_TEMPLATES, '*.txt')):
            rows = []
            with open(fname, encoding=None) as fp:
                titles = fp.readline().lower()
                titles = titles.strip().split('\t')
                for invalid_key in INVALID_KEYS:
                    if invalid_key in titles:
                        titles.pop(titles.index(invalid_key))
                for line in fp.readlines():
                    line = line.strip().split('\t')
                    row = dict([(a, try_int(b)) for a, b in zip(titles, line)])
                    rows.append(row)
            if len(rows):
                name = splitext(basename(fname))[0]
                template[name] = rows
        return template


    @property
    def templates(self):
        if not hasattr(self, '_templates'):
            self._templates = self._read_templates()
        return self._templates


    def create_with_templates(self, **options):
        profile_name = options.get('profile_name')
        if not profile_name:
            raise CommandError("You need to provide a profile_name name")
        co_ips = options.get('co_ips')
        if not co_ips:
            raise CommandError("No address specified, use -a x.x.x.x to specify an IP")

        if options.get('delete'):
            try:
                Profile.objects.get(name__iexact=profile_name).delete()
            except Profile.DoesNotExist:
                pass
        profile, _created = Profile.objects.get_or_create(name=profile_name)
        for ip_address in co_ips:
            comaster = profile.comasters.create(ip_address=ip_address,
                                                enabled=True)
            ais = {}
            for ied, iterlist in groupby(self.templates.ai, lambda d: d['ied_id']):
                ais[ied] = list(iterlist)
            for ied_args in self.templates.ied:
                data = filter_dict_fields(IED, ied_args)
                print ied_args
                print "Creando IED con ", data
                ied = comaster.ieds.create(**data)
                for sv_args in self.templates.sv:
                    data = filter_dict_fields(SV, sv_args)
                    ied.sv_set.create(**data)
                if ied.rs485_address == 1:
                    for di_args in self.templates.di:
                        data = filter_dict_fields(DI, di_args)
                        ied.di_set.create(**data)

                for ai_args in ais[ied.rs485_address]:
                    data = filter_dict_fields(AI, ai_args)
                    ied.ai_set.create(**data)
        for tag_data in self.templates['tag']:
            SVGElement.objects.get_or_create(**tag_data)
        for formula_data in self.templates['formulas']:
            Formula.objects.create(**formula_data)



    DEFAULT_EXCEL_TEMPLATE_GLOB = '../../doc/2013/EstructuraBDD-*.xls'

    def get_latest_excel(self):
        candidates = glob(self.DEFAULT_EXCEL_TEMPLATE_GLOB)
        candidates.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        latest = candidates[0]
        return latest

    def read_excel_template(self, excel_path=None):
        if not excel_path:
            excel_path = self.get_latest_excel()
        with xlrd.open_workbook(excel_path) as wb:
            print wb


    def handle_noargs(self, **options):
        return self.create_with_templates(**options)
        # TODO FINISH!
        """"""
        profile_name = options.get('profile_name')
        if not profile_name:
            raise CommandError("You need to provide a profile name")
        co_ips = options.get('co_ips')
        if not co_ips:
            raise CommandError("No address specified, use -a x.x.x.x to specify an IP")

        if options.get('delete'):
            try:
                Profile.objects.get(name__iexact=profile_name).delete()
            except Profile.DoesNotExist:
                print "Can't delete profile %s" % profile_name

        self.read_excel_template()
