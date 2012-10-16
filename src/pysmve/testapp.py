# encoding: utf-8

from flask import Flask
from flask import request

app = Flask(__name__)

# Serviro los archivos estáticos

@app.context_processor
def static_url():
    return dict(STATIC_URL = '/static/')


@app.route("/", methods=['GET', 'POST'])
def hello():
    if request.method == "GET":
        return """
        <html>
        <head>
        <script type="text/javascript" src="/static/js/jquery.js"></script>
        <link type="text/css" rel="stylesheet" href="/static/css/estilo.css"></link>
        </head>
        <body>
            <form method="GET" action="">
                Nombre: <input name="nombre" type="text"></br>
                Apellido: <input name="apellido" type="text"></br>
                <input type="submit" value="Enviar" name="enviar">
                <input type="submit" name="olvide_pass" value="Olvide mi contraseña">
            </form>
            
            <a href="/listado?cantidad=10" id="boton1">Link!</a>
            <a href="#" id="boton2">Obtener datos</a>
            
            <script>
                $('#boton1').click(function(){
                
                    var link = this; // El this en este contexto es es el link
                    
                    $.ajax('/ajax1', {
                        success: function(data){
                            $(link).after(data);
                        }
                    });
                    return false;
                });
                
                $('#boton2').click(function (){
                    $.ajax('/ajax2', {
                        success: function(data){
                            json = $.parseJSON(data);
                            console.log(data, json);
                        }
                    });
                    return false;
                
                });
            </script>
            
            
        </body>
        </html>
        
        """
    else:
        return """
            Tu nombre es: %s
            Tu apellido es: %s
        """ % (request.form['nombre'], request.form['apellido'] )

@app.route("/listado",methods=['GET', 'POST'])
def listado():
    
    cantidad = request.args.get('cantidad', 10)
    cantidad = int(cantidad)
    html = """
        <html>
        <head></head>
        <body>
    <ul>"""
    for i in range(cantidad):
        html += '<li>%d</li>' % i
    html += '</ul></body></html>'
    return html

@app.route('/ajax1')
def ajax1():
    return '''
        <p>Hola gente!</a>
    '''

def hacer_query():
    return ('Nahuel', 'Defosse', True, 28, )

@app.route('/ajax2')
def ajax2():
    from json import dumps
    datos = hacer_query()
    return dumps(datos)


        
if __name__ == "__main__":
    app.run(debug=True)