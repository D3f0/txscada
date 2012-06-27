from flask import Blueprint, render_template, abort

smve = Blueprint('smve', __name__,
                template_folder = 'templates')
                

# Test purposue
from random import seed, randrange
seed(os.getpid())
from utils.datatable import parseparams
from utils.decorators import stacktraceable
from utils.marshall import dumps


@smve.route("/")
#@stacktraceable
def index():
    return render_template("index.html")    

@smve.route('/valores/')
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

@smve.route('/eventos/')
def eventos():
	'''jQuery datatable inspired json data'''
	data = []
	#print request.values
	options = parseparams(request.values)
	#import ipdb; ipdb.set_trace()
	for i in xrange(options.get('display_length', 10)):
		data.append(["Evento", randrange(1, 10), randrange(1,20), randrange(1, 10)])
	return jsonify(dict(aaData = data))

@smve.route('/potencias_historicas/')
def potencias_historicas():
	from datetime import date, time, datetime, timedelta
	d = datetime.combine(date.today(), time(0, 0, 0))
	next = datetime.today() + timedelta(days=1)
	data = []
	while d < next:
		data.append([d, randrange(1,100)])
		d += timedelta(minutes=randrange(1,60))
	return dumps(dict(data=data))

@smve.route('/api/comaster/')
def comaster():
    return jsonify({'aaData': []})
    
@smve.route('/api/ucs/')
def ucs():
    data = []
    for i in range(randrange(5)):
        data.append([randrange(10),
                    randrange(10),
                    randrange(10),
                    randrange(10)])
    return jsonify({'aaData': data})