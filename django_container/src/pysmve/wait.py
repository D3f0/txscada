import sys
from socket import socket, error
import time


def main(args):
    try:
        host, port = args[-2:]
        port = int(port)
    except (ValueError, TypeError, IndexError) as e:
        sys.stderr.write("Usage: %s host:port. Error: %s" % (__name__, e))
        return 2
    address = (host, port)
    sock = socket()
    sock.settimeout(0.5)

    while True:
        try:
            sock.connect(address)
        except error:
            time.sleep(1)
            print("Retrying %s:%d" % address)
        else:
            return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))