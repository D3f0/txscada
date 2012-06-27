# encoding: utf-8
from pysmve import app
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
    print d
    return d
    
@app.template_filter('draw_table')
def draw_table(table=None, attributes = None, hide_columns = None, name = None):
    '''Renderiza una tabla de peewee conmo una jQuery Datatable
    generado configuración inicial'''
    from operator import attrgetter
    import json
    if not name:
        name = table._meta.model_name
    
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