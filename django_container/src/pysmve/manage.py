#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nguru.nguru.settings")
    # Running from the upper level needs to know how to import Django project
    # Do not remove despite settigs.py (settings/__init__.py) has more
    # sys.paths amendments
    sys.path.append(os.path.join(os.getcwd(), 'nguru'))
    sys.path.append(os.path.join(os.getcwd(), 'nguru', 'nguru'))
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
