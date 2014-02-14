from django.core.management.base import NoArgsCommand, CommandError
from optparse import make_option
import glob
import os
from os.path import abspath, join
import re

frame_regex = re.compile(r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})?[\w\:\s]+'
                         r'(?P<frame>FE ([0-9A-F]{2}\s?){8,512})', re.IGNORECASE)

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('-d', '--directory', default='.', dest='directory'),
        make_option('-p', '--log-pattern', default='*.log.*'),
        make_option('-D', '--default-comaster', default='192.168.2.40'),
    )

    def get_glob_expr(self):
        return join(abspath(self.options['directory']),
                    self.options['log_pattern'])

    def get_filenames(self):
        '''Returns file list, sorted'''
        names = glob.glob(self.get_glob_expr())
        names.sort(key=lambda x: os.stat(x).st_mtime)
        return names

    def build_comaster_map(self):
        from apps.mara.models import COMaster
        com_map = dict([ (c.ip_address, c) for c in COMaster.objects.all()])
        return com_map


    def handle_noargs(self, **options):

        # Memory leak
        #import guppy
        #from guppy.heapy import Remote
        #Remote.on()
        #import objgraph


        self.options = options

        counter = 0
        comaster_map = self.build_comaster_map()
        filenames = self.get_filenames()

        for n, filename in enumerate(filenames):
            print "%.f%%" % (100*n/float(len(filenames)))

            with open(filename, 'r') as fp:

                for n, line in enumerate(fp.readlines()):
                    match = frame_regex.search(line)
                    if match:
                        key = match.group('ip') or self.options['default_comaster']
                        comaster = comaster_map[key]
                        text_buffer = match.group('frame')
                        frame = str2frame(text_buffer)
                        if not has_events(frame):
                            continue

                        try:
                            comaster.process_frame(frame,
                                                   #update_states=False,
                                                   #calculate=False
                                                   )
                        except KeyboardInterrupt:
                            return

                        counter += 1
        print counter

def has_events(frame):
    payload = getattr(frame, 'payload_10', None)
    if payload and len(payload.event) > 0:
        return True
    return False


def str2frame(text_buffer):
    from protocols.constructs.structs import hexstr2buffer
    from protocols.constructs import MaraFrame

    buff = hexstr2buffer(text_buffer)
    return MaraFrame.parse(buff)