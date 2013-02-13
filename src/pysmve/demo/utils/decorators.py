def stacktraceable(f):
	def wrapped(*largs, **kwargs):
		try:
			return f(*largs, **kwargs)
		except Exception, e:
			from traceback import format_exc
			return "<pre>%s</pre>" % format_exc()
	return wrapped
