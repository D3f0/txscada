#!/usr/bin/env python
# encoding: utf-8
'''
Base de datos según la hoja IED-Alpha de MicroCNet-v17
'''

__all__ = ['AI', 'Energia', 'Evento', 'DI', 'VarSys']


import os
import sys
from os.path import join, dirname
from peewee import *

DB_FILE = join(dirname(__file__), 'database.db')
database = SqliteDatabase(DB_FILE)

class BaseModel(Model):
    class Meta:
        database = database


class COMaster(BaseModel):
    '''
    Modela un concentrador a ser consultado
    TODO: Falta apuntar el concentrador a un perfil, para poder versinar
    '''
    direccion = CharField(verbose_name=u"Direcci&oacute;n", unique=True)
    descripcion = CharField(verbose_name=u"Descripci&oacute;n")
    hablitado = BooleanField(default=False)
    port = IntegerField(verbose_name="Puerto TCP de conexion", default=9761)
    timeout = FloatField(default = 5.0, help_text="Tiempo que se espera por consulta antes de decretarlo muerto")
    poll_interval = FloatField(default = 5, help_text="Tiempo en segundos entre consultas") 
    
    def __unicode__(self):
        #return "<COMaser IP: %s Hab:%s>" % (self.direccion, self.hablitado)
        return "%s"  % self.direccion
    
    @property
    def varsys(self):
        return VarSys.filter(ied__co_master = self)
        
    @property
    def ais(self):
        return AI.filter(ied__co_master = self)
    
    @property
    def dis(self):
        return DI.filter(ied__co_master = self)

def iter_n_times(times=8):
    counter = 0
    while True:
        yield counter % times
        counter += 1


class IED(BaseModel):
    '''Descripcion del IED conectado a un comaster'''
    
    # Los puertos de digitales son de 16 bits
    PORT_WIDTH = 16
    
    co_master = ForeignKeyField(COMaster)
    offset = IntegerField()
    can_varsys = IntegerField(default=0, help_text="Cantidad de variables")
    can_dis = IntegerField(default=0, help_text=u"Cantidad de variables digitales")
    can_ais = IntegerField(default=0, help_text=u"Cantidad de variables analógicas")
    dir_485_ied = IntegerField(help_text="Dirección 485")
    
    
    def __unicode__(self):
        return ("CO:{co_master} Offset:{offset} VS:{can_varsys} AIs:{can_ais} DIs:{can_dis}" 
                " 485:{dir_485_ied}").format(
        co_master=self.co_master, offset=self.offset, can_varsys=self.can_varsys,
        can_ais=self.can_ais, can_dis=self.can_dis, dir_485_ied=self.dir_485_ied
        )
    
    @property
    def siblings(self):
        '''IED hermanos'''
        return self.co_master.ied_set.filter(offset__ne = self.offset)
        
    def crear_puertos_di(self, cant_ptos=1, pto_base=0):
        '''Crear puertos digitales'''
        for no_port in range(pto_base, cant_ptos):
            for no_bit in range(self.PORT_WIDTH):
                # Crear la DI
                parametro="D%.2d" % ((no_port * self.PORT_WIDTH) + no_bit)
                DI(ied=self, puerto=no_port, numero_de_bit=no_bit, parametro=parametro).save()

                
                
        
            

class MV(BaseModel):
    '''Basado en el tipo de dato Measured Value de IEC61850'''
    #class Meta:
    #    database = database
    #abstract = True
    
    ied = ForeignKeyField(IED)
    offset = IntegerField(default=0, help_text="Desplazamiento en la trama")
    
    def save(self, *largs, **kwargs):
        
        self.offset = self.filter(ied__co_master = self.ied.co_master).aggregate(Max('offset'))
        if self.offset is None:
            self.offset = 0
        else:
            self.offset += 1
        print "Creando %s con offset %s" % (self._meta.model_name, self.offset)
        
        return BaseModel.save(self, *largs, **kwargs)
        

class CMV(BaseModel):
    pass
    
        
class VarSys(MV):
    '''
    Nombre		VarSys		Calif	0	Normal
    Tipo		RealTime			1	stalled
    Tamaño		8			2	Calculada
    Unidad		bit	
    '''
    #ied = ForeignKeyField(IED)
    #offset = IntegerField()
    parametro = CharField()
    descripcion = CharField()
    unidad_de_medida = CharField(db_column="umedida")
    
    valor = IntegerField()
    

class DI(MV):
    '''
    Nombre		DIs		Calif	0	Normal
    Tipo		RealTime		1	stalled
    Tamaño		1				2	Calculada
    Unidad		bit				
    '''
    #ied = ForeignKeyField(IED)
    #offset = IntegerField()
    parametro = CharField(help_text="Valores D01 a D111")
    descripcion = CharField()
    puerto = IntegerField()
    numero_de_bit = IntegerField(db_column="nrobit")
    calificador = IntegerField(db_column="calif")
    valor = IntegerField()
    
    def save(self, *largs, **kwargs):
        
        cant_dis_ied = self.filter(ied__co_master = self.ied.co_master).count()
        if cant_dis_ied is None: cant_dis_ied = 0
        self.offset = cant_dis_ied // 8 # Frame length
        print "Creando %s con offset %s" % (self._meta.model_name, self.offset)
        
        return BaseModel.save(self, *largs, **kwargs)
    
class Evento(BaseModel):
	'''
	'''
	di = ForeignKeyField(DI)
	calificador = IntegerField(db_column="calif")
	timestamp = DateTimeField()
	valor = IntegerField()

    
class AI(MV):
	'''Analogicas digitales (valores de energia)
	'''
	#ied = ForeignKeyField(IED)
	#offset = IntegerField(db_column='umedida')
	parametro = CharField()
	descripcion = CharField()
	unidad_de_medida = CharField()
	Ke = FloatField()
	multip_asm = FloatField(default=1)
	divider = FloatField(default=1)
	relacion_tv = FloatField(db_column="reltv", default=12)
	relacion_ti = FloatField(db_column="relti", default=5)
	relacion_33_13 = FloatField(db_column="rel33-13", default=2.5)
	calificador = IntegerField(db_column="calif", default=0)
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




def get_models(base=None):
    '''Django like get_models'''
    if not base:
        base = BaseModel
    for subclass in base.__subclasses__():
        yield subclass
        for subsubclass in get_models(subclass):
            yield subsubclass

def crear_tablas():
    '''Crea los modelos definidos en el archivo'''
    for n, model in enumerate(get_models()):
        print "Creando clase", n+1, model._meta.model_name
        model.create_table(True)

def texto_tabulado_a_lista_enteros(texto):
    '''Separa texto pegado desde excel (separado por \t)
    en listas/tuplas de enteros'''
    salida = []
    for line in texto.split('\n'):
        line = line.strip()
        if not line: continue
        salida.append(map(int, line.split()))
    return salida
    
    
def crear_co_master_template(direccion=None, descripcion=None, habilitado=True):
    # TODO: Completar la función
    if not direccion: direccion = '192.168.1.97'
    
    
        

def cargar_tablas():
    
    master = COMaster(direccion = '192.168.1.97', descripcion="CO Master de Prueba",
                      hablitado = True)
    master.save()
    # Copiado y pegado del excel
    text_cfg = '''
    0	8	6	2	1
    1	4	4	4	2
    2	4	4	4	3
    3	4	4	4	4
    4	4	4	4	5
    '''
    configuracion = texto_tabulado_a_lista_enteros(text_cfg)
    PORT_WIDTH = 16
    for offset, canvarsys, candis, canais, dir485ied in configuracion:
        ied = IED(offset=offset, can_varsys = canvarsys,
                    can_dis = candis, can_ais = canais,
                    dir_485_ied = dir485ied, co_master = master)
        ied.save()
        
        if dir485ied == 1:
            # VarSys del IED 1 (el co master)
            VarSys(ied = ied, parametro="Calif", descripcion="Calificador", unidad_de_medida="unidad").save()
            VarSys(ied = ied, parametro="RateCountLoop", descripcion="", unidad_de_medida="Ciclos").save()
            VarSys(ied = ied, parametro="RateCountLoop2", descripcion="", unidad_de_medida="Ciclos").save()
            VarSys(ied = ied, parametro="Sesgo", descripcion="Sesgo (entero)", unidad_de_medida="ms").save()
            # DIS del CO Master
            ied.crear_puertos_di(3)
            
            AI(ied=ied, parametro="V", descripcion="Tensión barra 33K", unidad_de_medida="Kv", multip_asm=1, 
               divider=1, relacion_tv=1, relacion_ti=0, relacion_33_13=2.5).save()
            
        else:
            # Crear el VS
            VarSys(ied=ied, parametro="Sesgo", descripcion="Sesgo (entero)", unidad_de_medida="ms").save()
            VarSys(ied=ied, parametro="Calificador", descripcion="Calif Low/Errores High", unidad_de_medida="Ciclos").save()
            # Crear DIs
            ied.crear_puertos_di(1)
            # Crear AIs
            AI(ied=ied, parametro="P", descripcion=u"Potencia Activa", unidad_de_medida="Kw", multip_asm=1.09, 
               divider=1, relacion_tv=12, relacion_ti=5, relacion_33_13=2.5).save()
            AI(ied=ied, parametro="Q", descripcion=u"Potencia Reactiva", unidad_de_medida="Kvar", multip_asm=1.09, 
               divider=1, relacion_tv=12, relacion_ti=5, relacion_33_13=2.5).save()
            
    
    #configuracion = map(lambdas: s.strip().split(), configuracion)
    

    

def main(argv=sys.argv):
    '''Crear las tablas de la base'''
    from argparse import ArgumentParser
    parser = ArgumentParser("Modelos")
    parser.add_argument('-r', '--reset', default=False, 
	                       action="store_true")
    parser.add_argument('-c', '--create', default=False,
                        action="store_true")
    options = parser.parse_args()
    
    
    if options.reset:
        print "Creando la base de datos"
        os.unlink(DB_FILE)
        database.connect()
        crear_tablas()
        cargar_tablas()
        
    elif options.create:
        print "Creando tablas en la base"
        database.connect()
    else:
        print "Iniciando shell"
        from IPython import embed
        embed()
    
        
if __name__ == '__main__':
	main()