try:
	import argparse
except ImportError, e:
	from utils import argparse

parser = argparse.ArgumentParser(usage="Cada comando recibe argumentos spearados por comas. "
								"Ej: server:restart")
parser.add_argument('-r', '--reload', action = "store_true", default = False,
					help = "Use Flask run script instead of Twisted reactor loop. "
					"Useful for testing only the web application reload")
parser.add_argument('-P', '--profile', default="default",
					help="Default profile")
parser.add_argument('-p', '--port', default=4000, type=int,
					help="Port to bind the webserver to.")
parser.add_argument('command', nargs=1, default='server')
parser.add_argument('-l', '--logfile', default='smve.log',
                    help="File for logging output")
parser.add_argument('-L', '--file-level', default='INFO', nargs='?', dest='file_level',
                    help="File logging level ('CRITICAL', 'DEBUG', 'ERROR', 'FATAL', 'INFO', 'WARNING')")
parser.add_argument('-O', '--stdout-level', default='DEBUG', nargs='?', dest='stdout_level',
                    help="Stdout logging level ('CRITICAL', 'DEBUG', 'ERROR', 'FATAL', 'INFO', 'WARNING')")