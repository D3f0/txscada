from xml.sax.saxutils import XMLGenerator
import simplejson
import datetime
import decimal
from tornado.escape import _unicode

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

class DateTimeAwareJSONEncoder(simplejson.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        if isinstance(o, datetime.datetime):
            d = datetime_safe.new_datetime(o)
            return d.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            d = datetime_safe.new_date(o)
            return d.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(DateTimeAwareJSONEncoder, self).default(o)

class Emitter(object):
    """
    Super emitter. All other emitters should subclass
    this one. It has the `construct` method which
    conveniently returns a serialized `dict`. This is
    usually the only method you want to use in your
    emitter. See below for examples.
    """
    EMITTERS = { }

    def __init__(self, data):
        self.data = data
        
    def render(self):
        """
        This super emitter does not implement `render`,
        this is a job for the specific emitter below.
        """
        raise NotImplementedError("Please implement render.")
            
    @classmethod
    def get(cls, format):
        """
        Gets an emitter, returns the class and a content-type.
        """
        if cls.EMITTERS.has_key(format):
            return cls.EMITTERS.get(format)

        raise ValueError("No emitters found for type %s" % format)
    
    @classmethod
    def register(cls, name, klass, content_type='text/plain'):
        """
        Register an emitter.
        
        Parameters::
         - `name`: The name of the emitter ('json', 'xml', 'yaml', ...)
         - `klass`: The emitter class.
         - `content_type`: The content type to serve response as.
        """
        cls.EMITTERS[name] = (klass, content_type)
        
    @classmethod
    def unregister(cls, name):
        """
        Remove an emitter from the registry. Useful if you don't
        want to provide output in one of the built-in emitters.
        """
        return cls.EMITTERS.pop(name, None)

class XMLEmitter(Emitter):
    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            for item in data:
                xml.startElement("resource", {})
                self._to_xml(xml, item)
                xml.endElement("resource")
        elif isinstance(data, dict):
            for key, value in data.iteritems():
                xml.startElement(key, {})
                self._to_xml(xml, value)
                xml.endElement(key)
        else:
            xml.characters(unicode(data))

    def render(self, request):
        stream = StringIO.StringIO()
        
        xml = XMLGenerator(stream, "utf-8")
        xml.startDocument()
        xml.startElement("response", {})
        
        self._to_xml(xml, self.data)
        
        xml.endElement("response")
        xml.endDocument()
        
        return stream.getvalue()

Emitter.register('xml', XMLEmitter, 'text/xml; charset=utf-8')

class JSONEmitter(Emitter):
    """
    JSON emitter, understands timestamps.
    """
    def render(self, request):
        return simplejson.dumps(self.data, cls=DateTimeAwareJSONEncoder, ensure_ascii=False, indent=4)
    
Emitter.register('json', JSONEmitter, 'application/json; charset=utf-8')
