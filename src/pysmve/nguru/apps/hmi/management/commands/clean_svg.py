from __future__ import print_function
from django.core.management.base import CommandError, NoArgsCommand
from django.conf import settings
from django.db.models.loading import get_models
from django.db.models import FileField
from fabric.contrib.console import confirm
from fabric.colors import green, red
import os


def files_in_folder(start):
    for root, dirs, names in os.walk(start):
        for name in names:
            yield os.path.relpath(os.path.join(root, name), start)


class Command(NoArgsCommand):
    help = 'Removes unsused fileds'

    def handle_noargs(self, **options):

        existing_files = set(files_in_folder(settings.MEDIA_ROOT))

        referenced_fields = set()
        for model in get_models():
            if model._meta.app_label in ('south', 'django'):
                continue
            fname = lambda f: f.name
            is_filefiled = lambda f: isinstance(f, FileField)
            fields = map(fname, filter(is_filefiled, model._meta.fields))
            if not fields:
                continue

            for row in model.objects.values_list(*fields):
                for value in row:
                    referenced_fields.add(value)
        unused_files = (existing_files - referenced_fields)
        unused_files = map(lambda f: os.path.join(settings.MEDIA_ROOT, f),
                           unused_files)
        count = len(list(unused_files))
        if count:
            if confirm(red('Delete %d files?' % count)):
                map(os.unlink, unused_files)
        else:
            print(green("No files to remove :D"))
