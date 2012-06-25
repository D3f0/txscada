# encoding: utf-8

from flask import Flask, render_template, jsonify
from jinja2 import FileSystemLoader
import os
from utils.decorators import stacktraceable
from utils.marshall import dumps

ROOT_PATH = os.path.dirname(__file__)
template_path = 'templates'
app = Flask(__name__)
app.jinja_loader = FileSystemLoader(os.path.join(ROOT_PATH, template_path))

# Test purposue
from random import seed, randrange
seed(os.getpid())

@app.context_processor
def static_url():
    return dict(STATIC_URL = '/static/')

@app.route("/")
def index():
    #import ipdb; ipdb.set_trace()
    try:
        return render_template("index.html")
    except Exception as e:
        print e

@app.route('/valores')
@stacktraceable
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
	for i in xrange(10):
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