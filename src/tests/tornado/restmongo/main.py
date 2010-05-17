#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import simplejson
import pymongo
from rest.mongo import MongoCollectionHandler, MongoDocumentHandler

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class RESTApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
                    (r"^/", MainHandler),
                    (r"^/(?P<db>\w*)/(?P<collection>\w*)/(?P<document_id>[\w,\d]*)/$", MongoDocumentHandler, {'emitter_format': 'json'}),
                    (r"^/(?P<db>\w*)/(?P<collection>\w*)/\??.*$", MongoCollectionHandler, {'emitter_format': 'json'}),
        ]
        tornado.web.Application.__init__(self, handlers)
        
        # Have one global connection across all handlers
        self.connection = pymongo.Connection('localhost', 27017)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Rest and Mongodb")

def main():
    tornado.options.parse_command_line()
    application = RESTApplication()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
