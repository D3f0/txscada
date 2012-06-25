# encoding: utf-8

# Base de datos según la hoja IED-Alpha de MicroCNet-v17

from peewee import *

database = SqliteDatabase('database.db')

class BaseModel(Model):
    class Meta:
        database = database

class AIS(BaseModel):
	'''Analogicas digitales
	Nombre		AIs		Calif	0	Normal
	Tipo		RealTime			1	stalled
	Tamaño		16			2	Calculada
	Unidad		bit	
	'''
	direccion = IntegerField(db_column='dir')
	offset = IntegerField(db_column='umedida')
	parametro = CharField()
	descripcion = CharField()
	unidad_de_medida = CharField()
	Ke = FloatField()
	divider = FloatField()
	relacion_tv = FloatField(db_column="reltv")
	relacion_ti = FloatField(db_column="relti")
	relacion_33_13 = FloatField(db_column="rel33-13")
	calificador = IntegerField(db_column="calif")
	valor = IntegerField()

class Energia(BaseModel):
	'''
	Nombre		Energia		Calif	0	Normal
	Tipo		Hist				1	stalled
	Tamaño		10					2	Calculada
	Unidad		byte
	'''
	direccion = IntegerField(db_column='dir')
	offset = IntegerField()
	parametro = CharField()
	descripcion = CharField()
	unidad_de_medida = CharField(db_column="umedida")
	Ke = FloatField()
	divider = FloatField()
	relacion_tv = FloatField(db_column="reltv")
	relacion_ti = FloatField(db_column="relti")
	relacion_33_13 = FloatField(db_column="rel33-13")
	calificador = IntegerField(db_column="calif")
	valor = IntegerField()
	timestamp = DateTimeField()

class Evento(BaseModel):
	'''
	Nombre		Eventos		Calif	0	Normal
	Tipo		Hist				1	stalled
	Tamaño		10					2	Calculada
	Unidad		byte				
	'''
	direccion = IntegerField(db_column="dir")
	parametro = CharField()
	descripcion = CharField()
	puerto = IntegerField()
	numero_de_bit = IntegerField(db_column="nrobit")
	calificador = IntegerField(db_column="calif")
	timestamp = DateTimeField()
	valor = IntegerField()


class DIS(BaseModel):
	'''
	Nombre		DIs		Calif	0	Normal
	Tipo		RealTime		1	stalled
	Tamaño		1				2	Calculada
	Unidad		bit				
	'''
	direccion = IntegerField(db_column="dir")
	parametro = CharField()
	descripcion = CharField()
	puerto = IntegerField()
	numero_de_bit = IntegerField(db_column="nrobit")
	calificador = IntegerField(db_column="calif")
	valor = IntegerField()

class VarSys(BaseModel):
	'''
	Nombre		VarSys		Calif	0	Normal
	Tipo		RealTime			1	stalled
	Tamaño		8			2	Calculada
	Unidad		bit	
	'''
	direccion = IntegerField(db_column="dir")
	parametro = CharField()
	descripcion = CharField()
	unidad_de_medida = CharField(db_column="umedida")
	valor = IntegerField()



import sys
def main(argv=sys.argv):
	'''Crear las tablas de la base'''
	database.connect()
	for cls in BaseModel.__subclasses__():
		print cls.create_table(True)
    #import ipdb; ipdb.set_trace()    
        
if __name__ == '__main__':
	main()