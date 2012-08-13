# encoding: utf-8

from flask import Flask, render_template, jsonify, request
from jinja2 import FileSystemLoader
import os
from utils.decorators import stacktraceable
from utils.marshall import dumps
#import template_utils


ROOT_PATH = os.path.dirname(__file__)
template_path = 'templates'
app = Flask(__name__)
app.jinja_loader = FileSystemLoader(os.path.join(ROOT_PATH, template_path))

# Base de datos
import models

# Test purposue
from random import seed, randrange
seed(os.getpid())
from utils.datatable import parseparams
#--------------------------------------------------------------------
# Contex processors y cosas para los temapltes
#--------------------------------------------------------------------

@app.context_processor
def static_url():
    return dict(STATIC_URL = '/static/')

@app.context_processor
def publish_models():
    import peewee
    d = {}
    for name in dir(models): 
        obj = getattr(models, name)
        try:
            assert issubclass(obj, peewee.Model)
        except:
            pass
        d[name] = obj
    return d
    
@app.template_filter('draw_table')
def draw_table(table=None, attributes = None, hide_columns = None, name = None):
    '''Renderiza una tabla de peewee conmo una jQuery Datatable
    generado configuración inicial'''
    from operator import attrgetter
    import json
    if not name:
        name = table._meta.model_name
    if not attributes: attributes = ''
    attributes += ' flag="model-datatable" model="%s"' % name
    fields = [field for field in table._meta.fields.values()]
    fields.sort(key=attrgetter('_order'))
    ths = ''.join(['<th>%s</th>' % f.verbose_name for f in fields])
    table = '<table %s>%s</table>' % (attributes or '', '<thead><tr>%s</tr></thead>' % ths)
    # Script initial configuration
    obj = {
        'bProcessing': True,
        'bServerSide': True,
        'bJQueryUI': True,
    }
    
    script = '''<script type="text/javascript">
        if (typeof(datatables) == "undefined"){
            datatables = {};
        }
        datatables.%(name)s = %(conf)s;
        </script>''' % dict(conf=json.dumps(obj), name=name)
        
    return '\n'.join([table, script])
    


@app.route("/")
#@stacktraceable
def index():
    return render_template("index.html")
    

@app.route('/valores/')
def valores():
    '''Retorna valores'''
    rand_pot = lambda : "%.2f Kw" % (randrange(1,250)/10.)
    rand_pot_r = lambda : "%.2f KVa" % (randrange(1,250)/10.)
    rand_current = lambda : "%.2f KVa" % (randrange(1000,5000)/10.)
    return jsonify({
        # Potencia 
        'potencia-1': rand_pot(),
        'potencia-2': rand_pot(),
        'potencia-3': rand_pot(),
        'potencia-4': rand_pot(),
        # Potencias reactivas
        'potencia-r-1': rand_pot_r(),
        'potencia-r-2': rand_pot_r(),
        'potencia-r-3': rand_pot_r(),
        'potencia-r-4': rand_pot_r(),
        # Corrientes
        'corriente-1': rand_current(),
        'corriente-2': rand_current(),
        'corriente-3': rand_current(),
        'corriente-4': rand_current(),
        })

@app.route('/eventos/')
def eventos():
    '''jQuery datatable inspired json data'''
    data = []
    #print request.values
    options = parseparams(request.values)
    #import ipdb; ipdb.set_trace()
    for i in xrange(options.get('display_length', 10)):
        data.append(["Evento", randrange(1, 10), randrange(1,20), randrange(1, 10)])
    return jsonify(dict(aaData = data))

@app.route('/potencias_historicas/')
def potencias_historicas():
    from datetime import date, time, datetime, timedelta
    d = datetime.combine(date.today(), time(0, 0, 0))
    next = datetime.today() + timedelta(days=1)
    data = []
    while d < next:
        data.append([d, randrange(1,100)])
        d += timedelta(minutes=randrange(1,60))
    return dumps(dict(data=data))

@app.route('/api/comaster/')
def comaster():
    return jsonify({'aaData': []})

def dump(iterable, skip=None):
    if not skip: skip = []
    data = []
    for obj in iterable:
        names = [ name for name in obj._meta.fields.keys() if not name in skip ]
        fields = map(lambda name: (name, getattr(obj, name)), obj._meta.fields.keys())
        data.append(dict(fields))
    return data

@app.route('/api/ais/')
def analog_inputs():
    """docstring for analog_inputs"""
    from flask_peewee.serializer import Serializer
    from models import AI
    from json import dumps    
    return dumps(dump(AI.select(), skip=['ied']))


@app.route('/api/events/')
def events():
    '''Events'''
    from datetime import datetime
    aaData = [('Estación 1', '1', 'Descripcion %d' % d, datetime.now())
              for d in range(10)]
    return dumps(dict(aaData=aaData))