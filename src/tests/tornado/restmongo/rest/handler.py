from tornado.web import RequestHandler
from rest.emitters import Emitter

class RESTHandler(RequestHandler):
    MAPPED_METHODS = { 'GET': 'retrieve', 'POST': 'create', 'PUT': 'update', 'DELETE': 'delete' }

    def __init__(self, *args, **kwargs):
        emitter_format = kwargs.pop('emitter_format', 'json')
        super(RESTHandler, self).__init__(*args, **kwargs)
        
        self.emitter_class, ct = Emitter.get(emitter_format)
        self.set_header('Content-Type', ct)

    def retrieve(self, *args, **kwargs):
        raise HTTPError(405)

    def create(self, *args, **kwargs):
        raise HTTPError(405)

    def update(self, *args, **kwargs):
        raise HTTPError(405)

    def delete(self, *args, **kwargs):
        raise HTTPError(405)

    def write(self, chunk):
        emitter = self.emitter_class(chunk)
        super(RESTHandler, self).write(emitter.render(self.request))
    
    def _execute(self, transforms, *args, **kwargs):
        """Executes this request with the given output transforms."""
        self._transforms = transforms
        method = self.request.method
        try:
            if method not in self.MAPPED_METHODS.keys():
                raise HTTPError(405)
            # If XSRF cookies are turned on, reject form submissions without
            # the proper cookie
            if method == "POST" and self.application.settings.get("xsrf_cookies"):
                self.check_xsrf_cookie()
            self.prepare()
            if not self._finished:  
                function = getattr(self, self.MAPPED_METHODS[method])
                function(*args, **kwargs)
                if self._auto_finish and not self._finished:
                    self.finish()
        except Exception, e:
            self._handle_request_exception(e)