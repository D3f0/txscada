from collections import namedtuple
from optparse import make_option

from apps.hmi.models import (Formula, SVGElement)
from apps.mara.models import (IED, DI, AI, Profile)
from bunch import bunchify
from django.core.management.base import CommandError, NoArgsCommand
from django.utils.translation import ugettext_lazy as _
from apps.mara.utils import WorkBook
from logging import getLogger


result_type = namedtuple('Result', 'ok error total')
#from apps.hmi.models import SVGElement


logger = getLogger('excel_import')


def add_vs_to_comaster(comaster):
    '''VS or 'varsys' have the same structure to every IED
    so insted of defining them'''
    param_descriptions = (
        ("ComErrorL", "MOTIV -CoMaster"),
        ("ComErrorH", "No Implementado"),
        ("Sesgo L", "Sesgo (Entero)"),
        ("Sesgo H", "Sesgo (Entero)"),
        ("CalifL", "GaP del clock"),
        ("CalifH", "Error-Arranque UART"),
    )
    offset = 1
    for ied in comaster.ieds.order_by('offset'):
        ied.sv_set.all().delete()
        for param, description in param_descriptions:
            sv = ied.sv_set.create(
                offset=offset,
                param=param,
                description=description,
            )
            offset += 1
            logger.info("Added %s", sv)


def import_profile_from_workbook(profile, workbook, no_calculate=False,):
    """Command independent importer"""

    for comaster in profile.comasters.all():
        add_vs_to_comaster(comaster)

    ieds = IED.objects.filter(co_master__profile=profile)
    DI.import_excel(workbook, ieds=ieds)
    AI.import_excel(workbook, ieds=ieds)

    screens = profile.screens.all()
    SVGElement.import_excel(workbook, screens=screens)
    Formula.import_excel(workbook, screens=screens)

    if not no_calculate:
        ok, error = Formula.calculate()
        return result_type(ok, error, ok + error)
    return result_type(0, 0, Formula.objects.all().count())


def open_workbook(path):
    '''Opens workbook using and wraps it in special XLRD class'''

    try:
        return WorkBook(path, formatting_info=True)
    except IOError as e:
        msg = "File {path} could not be read or it's not an exce file {error}"
        msg.format(path=path, error=e)
        raise CommandError(msg)


def get_models_to_clear(model_list):
    for model in model_list:
        pass

class Command(NoArgsCommand):

    help_text = '''Import differences given a Excel file with just a few rows'''

    option_list = (
        make_option('-e', '--excel',
                    dest='workbook',
                    help=_("Excel file"),
                    default=''),
        make_option('-p', '--profile',
                    dest='profile_name',
                    help=_('Profile donde cargar las formulas'),
                    default='default',
                    ),
        make_option('-n', '--no-post-calculate',
                    dest='no_post_calculate',
                    default=True,
                    help=_('No calculate forumlas after import'),
                    ),
        make_option('-C', '--clear',
                    action='append',
                    dest='clear_models',
                    default=[],
                    help=_("Clear given models"),
                    )
    ) + NoArgsCommand.option_list

    def handle_noargs(self, **options):

        # Remote debugging

        options = bunchify(options)
        if options.clear_models:
            raise NotImplementedError(unicode(_("Model clear not implemented")))

        workbook = open_workbook(options.workbook)
        try:
            profile = Profile.objects.get(name=options.profile_name)
        except Exception as e:
            raise CommandError(e)

        result = import_profile_from_workbook(profile,
                                              workbook,
                                              no_calculate=options.no_post_calculate)
        if result.error:
            logger.warning(_("Errors in formulas: %2d") % result.error)
        logger.info(_("Formulas calculated OK: %2d") % result.ok)
        logger.info(_("Total: %2d") % result.total)
