#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import sys



def get_model_class(name, parent = None):
    pass


def main(argv = sys.argv):
    sys.path.append('..')
    os.environ["DJANGO_SETTINGS_MODULE"] = 'dscada/settings'
    from django.db import models
    pass


if __name__ == "__main__":
    sys.exit(main())
