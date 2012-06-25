import json
import datetime

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            return simplejson.JSONEncoder.default(self, obj)

def dumps(data, *largs, **kwargs):
	if len(largs) > 0 or len(kwargs) > 0:
		raise Exception("Unexpected arguments. Update function definition")
	return json.dumps(data, cls=JSONEncoder)

def main():
	
	print dumps({'date': datetime.datetime.now()})

if __name__ == '__main__':
	main()