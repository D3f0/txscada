from rest.handler import RESTHandler
from rest.emitters import Emitter, DateTimeAwareJSONEncoder
from pymongo.objectid import ObjectId, InvalidId
import simplejson

class MongoJSONEncoder(DateTimeAwareJSONEncoder):

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        else:
            return super(MongoJSONEncoder, self).default(o)

class MongoJSONEmitter(Emitter):
    def render(self, request):
        return simplejson.dumps(self.data, cls=MongoJSONEncoder, ensure_ascii=False, indent=4)
    
Emitter.register('json', MongoJSONEmitter, 'application/json; charset=utf-8')

class MongoCollectionHandler(RESTHandler):
    
    def retrieve(self, db, collection):
        db = self.application.connection[db]
        
        #TODO: Encontrar una forma mejor de hacer esto Esto es re peligros estoy evaluando lo que viene en la query
        criteria = db.eval(self.get_argument('criteria', '{}'))
        fields = db.eval(self.get_argument('fields', 'null'))
        skip = int(db.eval(self.get_argument('skip', '0')))
        limit = int(db.eval(self.get_argument('limit', '0')))
        
        col = db[collection]
        data = list(col.find(criteria, fields, skip, limit))
        self.write(data)
        
    def create(self, db, collection):
        db = self.application.connection[db]
        
        document = db.eval(self.request.body)
        
        if not document:
            raise HTTPError(405)
        
        col = db[collection]
        
        id = col.insert(document)
        self.write(id)

    def update(self, db, collection):
        db = self.application.connection[db]
        
        document = db.eval(self.request.body)
        criteria = db.eval(self.get_argument('criteria', '{}'))
        
        if not document or not criteria:
            raise HTTPError(405)
        
        col = db[collection]
        #TODO: hacer que multi sea opcional, validar que el ni el criterio ni el documento traigan id
        col.update(criteria, document, multi = True)
        #TODO: retornar la cantidad de elementos afectados
        self.write()
    
    def delete(self, db, collection):
        db = self.application.connection[db]
        
        criteria = db.eval(self.get_argument('criteria', '{}'))
        
        col = db[collection]
        
        col.remove(criteria)
        #TODO: retornar la cantidad de elementos afectados
        self.write()

class MongoDocumentHandler(RESTHandler):
    def prepare(self):
        pass
    
    def create_id(self, value):
        try:
            return ObjectId(value)
        except InvalidId:
            try:
                return int(value)
            except ValueError:
                return str(value)
    
    def retrieve(self, db, collection, document_id):
        db = self.application.connection[db]
        
        col = db[collection]
        data = col.find_one({'_id': self.create_id(document_id)})
        self.write(data)
        
    def update(self, db, collection, document_id):
        db = self.application.connection[db]
        
        document = db.eval(self.request.body)
        
        if not document:
            raise HTTPError(405)
    
        col = db[collection]
        
        col.update({'_id': self.create_id(document_id)}, document)
        self.write()
    
    def delete(self, db, collection, document_id):
        db = self.application.connection[db]
        
        col = db[collection]
        
        col.remove({'_id': self.create_id(document_id)})

        self.write()
