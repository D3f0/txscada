#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
Asegurarse de que solo exista una instancia de la aplicación en 
ejecución.
'''

from socket import socket
from select import select


def check_one_only():
    '''
    '''
    pass