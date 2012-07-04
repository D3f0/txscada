# encoding: utf-8
'''
Base de datos según la hoja IED-Alpha de MicroCNet-v17
'''

__all__ = ['AIS', 'Energia', 'Evento', 'DIS', 'VarSys']


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
        return AIS.filter(ied__co_master = self)
    
    @property
    def dis(self):
        return DIS.filter(ied__co_master = self)
    

class IED(BaseModel):
    '''Descripcion del IED conectado a un comaster'''
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

# class MV(BaseModel):
#     '''Basado en el tipo de dato Measured Value de IEC61850'''
#     class Meta:
#         database = database
#     ied = ForeignKeyField(IED)
#     offset = IntegerField(default=0, help_text="Desplazamiento en la trama")
#     
#     def get_next_offset(self):
#         pass
#     
#     def save(self, *largs, **kwargs):
#         print largs, kwargs
#         import ipdb; ipdb.set_trace()
#         super(MV, self).save(*largs, **kwargs)
    
class VarSys(BaseModel):
    '''
    Nombre		VarSys		Calif	0	Normal
    Tipo		RealTime			1	stalled
    Tamaño		8			2	Calculada
    Unidad		bit	
    '''
    ied = ForeignKeyField(IED)
    offset = IntegerField()
    parametro = CharField()
    descripcion = CharField()
    unidad_de_medida = CharField(db_column="umedida")
    
    valor = IntegerField()
    
    def save(self, *largs, **kwargs):
        
        self.offset = self.filter(ied__co_master = self.ied.co_master).aggregate(Max('offset'))
        if self.offset is None:
            self.offset = 0
        else:
            self.offset += 1
        print "Creando %s con offset %s" % (self.__class__.__name__, self.offset)
        
        return super(self.__class__, self).save(*largs, **kwargs)


class DIS(BaseModel):
    '''
    Nombre		DIs		Calif	0	Normal
    Tipo		RealTime		1	stalled
    Tamaño		1				2	Calculada
    Unidad		bit				
    '''
    ied = ForeignKeyField(IED)
    parametro = CharField()
    offset = IntegerField()
    descripcion = CharField()
    puerto = IntegerField()
    numero_de_bit = IntegerField(db_column="nrobit")
    calificador = IntegerField(db_column="calif")
    valor = IntegerField()
    
    def save(self, *largs, **kwargs):
        
        self.offset = VarSys.filter(ied__co_master = self.ied.co_master).aggregate(Max('offset'))
        if self.offset is None:
            self.offset = 0
        else:
            self.offset += 1
        print "Creando varsys con offset", self.offset
        
        return super(VarSys, self).save(*largs, **kwargs)
        
class Evento(BaseModel):
	'''
	'''
	di = ForeignKeyField(DIS)
	calificador = IntegerField(db_column="calif")
	timestamp = DateTimeField()
	valor = IntegerField()

    
class AIS(BaseModel):
	'''Analogicas digitales (valores de energia)
	'''
	ied = ForeignKeyField(IED)
	offset = IntegerField(db_column='umedida')
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





def crear_tablas():
    bases = [BaseModel, ]
    for base in bases:
        classes = base.__subclasses__()
        for n, cls in enumerate(classes):
            print "Creando clase", n+1, "de", len(classes)
            sys.stdout.flush()
            cls.create_table(True)
    print
def cargar_tablas():
    
    master = COMaster(direccion = '192.168.1.97', descripcion="CO Master de Prueba",
                      hablitado = True)
    master.save()
    
    configuracion = '''
    0	8	6	2	1
    1	4	4	4	2
    2	4	4	4	3
    3	4	4	4	4
    4	4	4	4	5
    '''
    configuracion = map(lambda s: s.strip(), configuracion.split('\n'))
    configuracion = filter(len, configuracion)
    configuracion = map(lambda s: map(int, s.split()), configuracion)
    
    offset = None
    for offset, canvarsys, candis, canais, dir485ied in configuracion:
        ied = IED(offset=offset, can_varsys = canvarsys,
                    can_dis = candis, can_ais = canais,
                    dir_485_ied = dir485ied, co_master = master)
        ied.save()
        
        if dir485ied == 1:
            
            VarSys(ied = ied, parametro="Calif", descripcion="Calificador", unidad_de_medida="unidad").save()
            VarSys(ied = ied, parametro="RateCountLoop", descripcion="", unidad_de_medida="Ciclos").save()
            VarSys(ied = ied, parametro="RateCountLoop2", descripcion="", unidad_de_medida="Ciclos").save()
            VarSys(ied = ied, parametro="Sesgo", descripcion="Sesgo (entero)", unidad_de_medida="ms").save()
        else:
            pass
    for i in IED.select():
        print i
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