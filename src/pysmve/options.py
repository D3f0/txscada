try:
	import argparse
except ImportError, e:
	from utils import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--reload', action = "store_true", default = False,
					help = "Use Flask run script instead of Twisted reactor loop. "
					"Useful for testing only the web application reload")

parser.add_argument('-p', '--port', default=4000, type=int,
					help="Port to bind the webserver to.")
parser.add_argument('command', nargs=1, default='server')
