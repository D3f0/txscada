Proyecto de SCADA con Python
============================

Código de proyecto de investigación **Microcontroladores e Internet** (2008-2010) y **Procesamiento digital de Señales Eléctricas, Protocolos y Aplicaciones WEB** (2013-2015) desarrollados en la Universidad Nacional
de la Patagonia, San Juan Bosco.

La carpeta ``src/pysmve`` contiene el código fuente del proyecto Medición de Variables Eléctricas y
la carpeta ``src/dsem`` del sistema de semaforización.


SMVE
----

Obtención del código fuente
***************************

El repositorio se encuentra mantenido mediante la herramineta Git, para obtenerlo es necesario
disponer de la utilidad ``git`` y ejecutar la siguiente orden::

	git clone https://github.com/D3f0/txscada.git


Base de datos
*************

Se ha utlizado Sqlite, MySQL durante etapas primigenias del proyecto, pero
se descidió utilizar Postgres diebido a la velocidad de inserción y
las herramientas de administración.

Para instalar postgres en Ubuntu::

	sudo apt-get install postgresql pgadmin3

Para trabajar de manera cómoda se recomienda crear un usuario Postgres::

	sudo su postgres -c "createuser $(whoami)"

Luego editar ``/etc/postgresql/9.1/main/pg_hba.conf`` y editar las primeras
lineas no comentadas para que se vean de la siguiente manera::

	# "local" is for Unix domain socket connections only
	local   all             all                                     trust
	# IPv4 local connections:
	host    all             all             127.0.0.1/32            trust

Luego reiniciar el servidor de base de datos y no necesitaríamos proveer
un password para ingreso local al servidor de base de datos y podremos
crear la base de datos como sigue::

	psql postgres # Conexión con la db postgres
	psql (9.2.2, servidor 9.1.4)
	Digite «help» para obtener ayuda.

	postgres=# 

Luego podemos crear una base de datos como sigue::

	postgres=# create database txscada;
	postgres=# GRANT ALL PRIVILEGES ON txscada TO myuser;

Dónde ``myuser`` debe ser nuestro nombre de usuario (creado en el createuser).



Ambiente de trabajo
*******************

Para poder probar el proyecto se debe crear un ambiente Python mediante
la herramienta *virtualenv*, para no interferir con los paquetes del sistema
y deslindar del desarrollo el uso del superusuario.
Para instalar *virtualenv* en Ubunutu realizar los siguientes pasos (serán
los unicos donde usaremos privilegios de administrador mediante sudo)::

	
	sudo apt-get install python-setuptools 

	sudo easy_install pip

	sudo pip install virtualenv virtualenvwrapper

	# Si usamos bash (averiguar con ps)
	echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
	# Si usamos zsh u otro shell, agregar al final del .zshrc o archivo de configuración
	# de usuario

Luego cerrar la terminal con ``^-D`` y inicar una nueva para que tome los cambios y luego::
	
	mkvirtualenv txscada
	whcih python  # debería dar una ruta en nuestro $HOME

Para entrar en el virtualen nuevamente::

	workon txscada

Para salir del virtualenv (y volver al intérprete de Python del sistema)::

	deactivate 

Para instalar un paquete dentro del virutalenv::

	pip install paquete


Un paso opcinal es editar el archivo ``~/.virtualenvs/txscada/bin/postactivate``
y agregar la linea cd ``/lugar/donde/tengo/el/codigo/del/proyecto/src/txscada`` para
que cada vez que hagamos ``workon txscada`` se cambie de manera automática a la carpeta
del proyecto.

Instalación de los paquetes en el virtualenv
********************************************

Para instalar los paquetes del proyecto en el virtualenv se debe reazliar la siguiente
orden::

	workon txscada
	cd /ruta/del/hacia/txscada/src/pysmve
	pip install -r requirements/develop.txt

Esto debería instalar todas las librerías necesarias para el proyecto en el virtualenv
``txscada``.


Freezado de librerías
*********************

Cuando se instala una librería en el virtualenv fuera de las que están en develop.txt
es recomendable ejecutar fab freeze para que el archivo se actualice y luego commitearlo
al repositorio para que el resto de los desarrolladores puedan instalarla, sobre todo
cuando se trabajan con paquetes *editables*, es decir que son tomados de un repositrio
git/svn/hg.

