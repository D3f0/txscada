from collections import namedtuple
from optparse import make_option

from apps.hmi.models import (Color, Formula, SVGElement, SVGPropertyChangeSet,
                             SVGScreen)
from apps.mara.models import (SV, IED,
                              Action, COMaster, ComEventKind, EventDescription,
                              EventText, Profile)
from bunch import bunchify
from django.core.management.base import CommandError, NoArgsCommand
from django.utils.translation import ugettext_lazy as _
from apps.mara.utils import WorkBook
from logging import getLogger


result_type = namedtuple('Result', 'ok error total')
#from apps.hmi.models import SVGElement


logger = getLogger('excel_import')


def import_profile_from_workbook(profile, workbook, no_calculate=False,):
    """Command independent importer"""

    # Process COMaster for profile
    ieds = IED.objects.filter(co_master__profile=Profile.objects.get())

    # Update
    #SV.import_excel(workbook, ieds=ieds)
    #svg_elements = SVGElement.objects.filter(screen__profile=profile)
    SVGElement.import_excel(workbook, screens=profile.screens.all())

    #Formula.import_excel(workbook, screens=profile.screens.all())

    if not no_calculate:
        ok, error = Formula.calculate()
        return result_type(ok, error, ok + error)
    return result_type(0, 0, Formula.objects.all().count())


def open_workbook(path):
    '''Opens workbook using and wraps it in special XLRD class'''

    try:
        return WorkBook(path, formatting_info=True)
    except IOError as e:
        raise CommandError(_("File %s could not be read or it's not an "
                           "excel file (%s)") % (path, e))


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
