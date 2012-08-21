#!/usr/bin/env python
# encoding: utf-8
'''
Base de datos según la hoja IED-Alpha de MicroCNet-v17
'''

__all__ = ['AI', 'Energy', 'Event', 'DI', 'VarSys', 'BaseModel']


import os
import sys
from os.path import join, dirname
from datetime import datetime

from peewee import (Model, 
				SqliteDatabase,
				DateTimeField,
				CharField, 
				FloatField, 
				IntegerField,
				BooleanField, 
				ForeignKeyField, 
				Max,
				DoesNotExist,
				create_model_tables,
				)
from peewee import MySQLDatabase, PostgresqlDatabase
from protocols import constants as mara

#DB_FILE = join(dirname(__file__), 'database.db')
#database = SqliteDatabase(DB_FILE)

#database = MySQLDatabase('smve', user='root', passwd='root')

database = PostgresqlDatabase('smve', user='postgres')

class BaseModel(Model):
	class Meta:
		database = database
		
		
class Profile(BaseModel):
	'''
	Solo hay un perfil activo y de el depende toda 
	la configuracion activa. Se pueden copiar los 
	perfiles para poder hacer pruebas o edici´on.
	'''
	def __init__(self, *largs, **kwargs):
		super(Profile, self).__init__(*largs, **kwargs)
		kwargs.setdefault('fecha', datetime.now())
		
	name = CharField(max_length=120)
	version = FloatField(default=1.0)
	date = DateTimeField()
	
	def copy(self, new_name):
		pass
	
	@classmethod
	def by_name(cls, name):
		'''Get profile by name or None if it does not exist'''
		try:
			return cls.get(name=name)
		except DoesNotExist:
			return None

class COMaster(BaseModel):
	'''
	Modela un concentrador a ser consultado
	TODO: Falta apuntar el concentrador a un perfil, para poder versinar
	'''
	profile = ForeignKeyField(Profile, help_text="Perfil asociado al master")
	address =  CharField(unique=True, default=mara.DEFAULT_COMASTER_ADDR, verbose_name=u"Direcci&oacute;n")
	description = CharField(verbose_name=u"Descripci&oacute;n")
	enabled = BooleanField(default=False)
	port = IntegerField(verbose_name="Puerto TCP de conexion", default=mara.DEFAULT_COMASTER_PORT)
	timeout = FloatField(default=mara.DEFAULT_TIMEOUT, help_text="Tiempo que se espera por consulta antes de decretarlo muerto")
	poll_interval = FloatField(default=mara.DEFAULT_POLL_INTERVAL, help_text="Tiempo en segundos entre consultas") 
	sequence = IntegerField(verbose_name="Mara sequence number", default=mara.MAX_SEQ)
	source = IntegerField(verbose_name="Default 485 source address", default=0)
	dest   = IntegerField(verbose_name="COMaster address to poll")
	
	def __unicode__(self):
		#return "<COMaser IP: %s Hab:%s>" % (self.address, self.enabled)
		return "%s"	 % self.address
	
	#===========================================================================
	# FIXME Make better order cirteria, creation counter?
	#===========================================================================
	@property
	def varsys(self):
		return VarSys.filter(ied__co_master=self).order_by('id')
		
	@property
	def ais(self):
		return AI.filter(ied__co_master=self).order_by('id')
	
	@property
	def dis(self):
		return DI.filter(ied__co_master=self).order_by('param')


class IED(BaseModel):
	'''Descripcion del IED conectado a un comaster'''
	
	# Los puertos de digitales son de 16 bits
	PORT_WIDTH = 16

	co_master = ForeignKeyField(COMaster)
	offset = IntegerField()
	can_varsys = IntegerField(default=0, help_text="Cantidad de variables")
	can_dis = IntegerField(default=0, help_text=u"Cantidad de variables digitales")
	can_ais = IntegerField(default=0, help_text=u"Cantidad de variables analógicas")
	addr_485_IED = IntegerField(help_text="Dirección 485")
	
	
	def __unicode__(self):
		return ("CO:{co_master} Offset:{offset} VS:{can_varsys} AIs:{can_ais} DIs:{can_dis}" 
			" 485:{addr_485_IED}").format(
			co_master=self.co_master, offset=self.offset, can_varsys=self.can_varsys,
			can_ais=self.can_ais, can_dis=self.can_dis, addr_485_IED=self.addr_485_IED
			)
	
	@property
	def siblings(self):
		'''IED hermanos'''
		return self.co_master.ied_set.filter(offset__ne=self.offset)

	def crear_varsys(self, cantidad,):
		"""docstring for crear_varsys"""
		raise NotImplementedError
		
			
	def build_di_ports(self, cant_ptos=1, pto_base=0):
		'''Crear puertos digitales'''
		# Función de conveniencia
		for no_port in range(pto_base, cant_ptos):
			for no_bit in range(self.PORT_WIDTH):
				# Crear la DI
				param = "D%.2d" % ((no_port * self.PORT_WIDTH) + no_bit)
				
				DI(ied=self, port=no_port, bit=no_bit, param=param).save()
				
			
				
		
			

class MV(BaseModel):
	'''Based on Measured Value from IEC61850 Standard'''
	#class Meta:
	#	 database = database
	#abstract = True

	ied = ForeignKeyField(IED)
	offset = IntegerField(default=0, help_text="Offset in Mara frame")

	def save(self, *largs, **kwargs):
		if not self.offset:
			self.offset = self.filter(ied__co_master=self.ied.co_master).aggregate(Max('offset'))
			if self.offset is None:
				self.offset = 0
			else:
				self.offset += 1
			print "Creating %s with offset: %s" % (self._meta.model_name, self.offset)

		return BaseModel.save(self, *largs, **kwargs)
		
	
		
class VarSys(MV):
	'''
	Nombre		VarSys		Calif	0	Normal
	Tipo		RealTime			1	stalled
	Tamaño		8			2	Calculada
	Unidad		bit	
	'''
	#ied = ForeignKeyField(IED)
	#offset = IntegerField()
	param = CharField()
	description = CharField()
	unit = CharField(db_column="umedida")
	
	valor = IntegerField()
	
	def __unicode__(self):
		"""Unicode"""
		return "%s %s %s" % (self.offset, self.param, self.description)
	

class DI(MV):
	'''
	Nombre		DIs		Calif	0	Normal
	Tipo		RealTime		1	stalled
	Tamaño		1				2	Calculada
	Unidad		bit				
	'''
	#ied = ForeignKeyField(IED)
	#offset = IntegerField()
	param = CharField(help_text="Valores D01 a D111")
	description = CharField()
	port = IntegerField()
	bit  = IntegerField(help_text="Bit number")
	q = IntegerField(db_column="q", help_text="Quality")
	value = IntegerField()
	
	def save(self, *largs, **kwargs):
		'''Guardar una digital'''
		if not self.offset:
			cant_dis_ied = self.filter(ied__co_master=self.ied.co_master).count()
			if cant_dis_ied is None: cant_dis_ied = 0
			self.offset = cant_dis_ied // 8 # Frame length
			print "Creating %s with offset: %s" % (self._meta.model_name, self.offset)

		return BaseModel.save(self, *largs, **kwargs)
	
	def __unicode__(self):
		values = [self.port, self.bit, self.param, self.description or "No desc", self.value]
		return " ".join(map(str, values))
	
	class Meta:
		indexes	 = (
			((), True)
		)
class Event(BaseModel):
	'''
	'''
	di = ForeignKeyField(DI)
	timestamp = DateTimeField()
	subsec = FloatField(default=0)
	q = IntegerField(db_column="calif")
	value = IntegerField()

	
class AI(MV):
	'''Analogicas digitales (valores de energia)
	'''
	#ied = ForeignKeyField(IED)
	#offset = IntegerField(db_column='umedida')
	param = CharField(max_length=5)
	description = CharField()
	unit = CharField(max_length=3)
	#Ke = FloatField()
	multip_asm = FloatField(default=1.09)
	divider = FloatField(default=1)
	relacion_tv = FloatField(db_column="reltv", default=12)
	relacion_ti = FloatField(db_column="relti", default=5)
	relacion_33_13 = FloatField(db_column="rel33-13", default=2.5)
	calificador = IntegerField(db_column="calif", default=0)
	value = IntegerField()
	
	@property
	def val(self):
		return self.value * self.multip_asm #* self.divider * self.relacion_tv * self.relacion_ti * self.relacion_33_13
	
	@property
	def human_value(self):
		return "%.3f %s" % (self.val, self.unit)
	
	def __unicode__(self):
		values = [self.description, self.human_value]
		return u" ".join(map(unicode, values))
		
	
class Energy(BaseModel):
	'''
	Nombre		Energia		Calif	0	Normal
	Tipo		Hist				1	stalled
	Tamaño		10					2	Calculada
	Unidad		byte
	'''
	ied = ForeignKeyField(IED)
	address = IntegerField()
	channel = IntegerField()
	offset = IntegerField()
	param = CharField()
	description = CharField()
	unit = CharField()
	Ke = FloatField()
	divider = FloatField()
	relacion_tv = FloatField(db_column="reltv")
	relacion_ti = FloatField(db_column="relti")
	relacion_33_13 = FloatField(db_column="rel33-13")
	q = IntegerField()
	value = IntegerField()
	timestamp = DateTimeField()
	
	@property
	def val(self):
		return self.value * self.multip_asm * self.divider * self.relacion_tv * self.relacion_ti * self.relacion_33_13
	
	@property
	def human_value(self):
		return "%.3f %s" % (self.val, self.unit)



def get_models(base=None):
	'''Django like get_models'''
	if not base:
		base = BaseModel
	for subclass in base.__subclasses__():
		yield subclass
		for subsubclass in get_models(subclass):
			yield subsubclass

def create_tables():
	'''Crea los modelos definidos en el archivo'''
	for n, model in enumerate(get_models()):
		print "Creating class", n + 1, model._meta.model_name
		model.create_table(True)

def tab_formatted2int_list(text):
	'''Converts text pasted from excel (using \t as separator)
	into a int list'''
	output = []
	for line in text.split('\n'):
		line = line.strip()
		if not line: continue
		output.append(map(int, line.split()))
	return output
		

def populate_tables(name, list_of_data):
	print "Creating profile: %s with (%d) hosts" % (name, len(list_of_data))
	profile = Profile(name=name, date=datetime.now())
	profile.save()
	for data in list_of_data:
		insert_comaster(profile, data)
	
def insert_comaster(profile, data):
	''' Creates one comaster with its configuration'''
	data.update(profile=profile,
				enabled=True,
				)
	assert 'address' in data, "Falta la dirección del COMaster"
	comaster = COMaster(**data)
					#profile=profile,
					#address=address, #   
					#description="CO Master for %s" % address.split('.')[-1],
					#enabled=True
					#)
	comaster.save()
	# Copiado y pegado del excel
	text_cfg = '''
	0	8	6	2	1
	1	4	2	4	2
	2	4	2	4	3
	3	4	2	4	4
	4	4	2	4	5
	'''
	config = tab_formatted2int_list(text_cfg)
	for offset, canvarsys, candis, canais, addr_485_IED in config:
		ied = IED(offset=offset, can_varsys=canvarsys,
					can_dis=candis, can_ais=canais,
					addr_485_IED=addr_485_IED, co_master=comaster)
		ied.save()
		# ------------------------------------------------------------------
		# TODO: Generar una configuración mejor, quizás pasando a un crear_var_sys
		# -----------------------------------------------------------from datetime import datetime-------
		
		if addr_485_IED == 1:
			# VarSys del IED 1 (el co master)
			VarSys(ied=ied, param="Calif", description="Calificador", unit="unidad").save()
			VarSys(ied=ied, param="RateCountLoop", description="", unit="Ciclos").save()
			VarSys(ied=ied, param="RateCountLoop2", description="", unit="Ciclos").save()
			VarSys(ied=ied, param="Sesgo", description="Sesgo (entero)", unit="ms").save()
			# DIS del CO Master
			ied.build_di_ports(3)
			
			AI(ied=ied, param="V", description=u"Tensión barra 33K", unit="Kv", multip_asm=1,
			  divider=1, relacion_tv=1, relacion_ti=0, relacion_33_13=2.5).save()
			
		else:
			# Crear el VS
			VarSys(ied=ied, param="Sesgo", description="Sesgo (entero)", unit="ms").save()
			VarSys(ied=ied, param="Calificador", description="Calif Low/Errores High", unit="Ciclos").save()
			# Crear DIs
			ied.build_di_ports(1)
			# Crear AIs
			AI(ied=ied, param="P", description=u"Potencia Activa", unit="Kw", multip_asm=1.09,
			  divider=1, relacion_tv=12, relacion_ti=5, relacion_33_13=2.5).save()
			AI(ied=ied, param="Q", description=u"Potencia Reactiva", unit="Kvar", multip_asm=1.09,
			  divider=1, relacion_tv=12, relacion_ti=5, relacion_33_13=2.5).save()

if __name__ == "__main__":
	# Minimal syncdb
	from IPython import embed; embed()
