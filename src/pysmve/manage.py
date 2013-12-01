#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nguru.nguru.settings")
    # Monkey patch settings
    sys.path.append(os.path.join(os.getcwd(), 'nguru'))
    sys.path.append(os.path.join(os.getcwd(), 'nguru', 'nguru'))


    #os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nguru.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
