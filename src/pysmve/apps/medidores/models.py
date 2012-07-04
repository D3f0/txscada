from peewee import *

class BaseModel(Model):
    class Meta:
        database = None
        
        
class Perfil(BaseModel):
    activo = BooleanField()
    nombre = CharField()
    
    
        
class Concentrador(BaseModel):
    perfil = ForeignKeyField(Perfil)
    direccion = CharField() # Direcci´on IP
    nombre = CharField()    # Nombre para mostrar
    cantidad_IEDs = IntegerField() # Cantidad de IEDs
    
    
class IED(BaseModel):
    concentrador = ForeignKeyField(Concentrador)
    dir485          = IntegerField()
    cantidad_VarSys = IntegerField()
    cantidad_DIs    = IntegerField()
    cantidad_AIs    = IntegerField()
    
    
class CurrentVarSys(BaseModel):
    #concentrador = ForeignKeyField(Concentrador)
    ied          = ForeignKeyField(IED)
    direccion    = IntegerField()
    parametro    = CharField()
    descripcion  = CharField()
    unidad_de_medida = CharField()
    valor        = IntegerField()
    
class CurrentDIs(BaseModel):
    ied         = ForeignKeyField(IED)
    parametro   = CharField()
    descripcion = CharField()
    puerto      = IntegerField()
    bit         = IntegerField()
    calificador = IntegerField()
    estado      = IntegerField()
    
class CurrentAIs(BaseModel):
    ied         = ForeignKeyField(IED)
    frame_offset = IntegerField()
    parametro = ForeignKeyField(Parametro)
    descripcion = CharField()
    unidad      = CharField()
    cte_ke      = FloatField()
    cte_multi_asm = IntegerField()
    cte_rel_tv    = IntegerField()
    cte_rel_33_13 = FloatField()
    calif = IntegerField()
    valor = IntegerField()
    