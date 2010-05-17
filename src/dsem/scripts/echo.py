#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
from socket import socket, SHUT_RDWR, error
from optparse import OptionParser

#DESTINO = ('192.168.1.8', 9761)

def parse_args(args):
    parser = OptionParser()
    parser.add_option('-H', '--host', dest="host", type=str,
                      help="Host al cual conectarse", default="192.168.1.8")
    parser.add_option('-p', '--port', dest="port",type=int,
                      help="Puerto al cual conectarse", default="9761")
    opts, args = parser.parse_args(args[1:])
    return opts

def main(argv = sys.argv):
    cfg = parse_args(argv)
    s = socket()
    s.settimeout(2.0)
    try:
        s.connect((cfg.host, cfg.port))
    except KeyboardInterrupt:
        s.shutdown(SHUT_RDWR)
        print "Terminando por señal de interrupcion"
        return -2
    except error, e:
        print "Error en el socket:", e
        return 1
    
    # Volvemos no bloqueante al socket
    s.settimeout(None)
    while True:
        try:
            cadena = s.recv(1024)
        except KeyboardInterrupt, e:
            sys.stderr.write("\nTerminando por señal de finalización\n")
            s.shutdown(SHUT_RDWR)
            s.close()
            return 1

        for x in cadena:
            print ('%.2x' % ord(x)).upper(),
        print

        sys.stdout.flush()
        s.send(cadena)

if __name__ == "__main__":
    sys.exit(main())
