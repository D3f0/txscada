# -*- coding: utf-8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.web
from os.path import join, dirname
import functools
import os,fcntl

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #self.write("Hello, world")
        self.render("index.html", data = self.application.from_mouse)
        
settings = dict(
template_path=join(dirname(__file__), "templates"),
           )

application = tornado.web.Application([
    (r"/", MainHandler),
    ], **settings)
    
application.from_mouse = 'NADA'

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    
    def connection_ready(sock, fd, events):
        data = sock.read()
        application.from_mouse = "/".join([str(ord(c)) for c in data])

    file = open('/dev/psaux', 'r')
    
    fd = file.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    
    io_loop = tornado.ioloop.IOLoop.instance()
    callback = functools.partial(connection_ready, file)
    io_loop.add_handler(file.fileno(), callback, io_loop.READ)
    io_loop.start()