# -*- coding: utf-8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.web
from os.path import join, dirname

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #self.write("Hello, world")
        self.render("index.html")
        
settings = dict(
template_path=join(dirname(__file__), "templates"),
           )

application = tornado.web.Application([
    (r"/", MainHandler),
    ], **settings)
            
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()