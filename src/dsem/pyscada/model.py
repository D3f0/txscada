#! /usr/bin/env python
# -*- encoding: utf-8 -*-

__all__ = ('metadata','CO', 'UC', 'SV', 'DI', 'AI',  'EV', 
           'Esquina',
           'Esquina_Calles', 'Calle',
           
           
           'EV_Descripcion', )
from sqlalchemy import *

#from pyscada.db_types import EnumType
from sqlalchemy.databases.mysql import MSEnum 
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.schema import MetaData, CheckConstraint
from sqlalchemy.orm import mapper, relation, validates
from sqlalchemy.orm.session import sessionmaker
# Tipos generales
from sqlalchemy.types import *
# Tipos particulares
from sqlalchemy.databases import mysql


metadata = MetaData()

LONG_DESCRIPCION = 250

#===============================================================================
# Concentrador
#===============================================================================

    
tabla_co = Table('CO', metadata,
                 
           # Este campo no tiene sentido
           #Column('id', Integer, primary_key = True),
           
           Column('id_CO', Integer, primary_key = True),
           # Direccion IP del concentrador
           Column('ip_address', String(15), unique = True, nullable = False),
           Column('hab', Boolean,  nullable = False),
           
           # Timeout
           Column('t_out', Float(presicion=3),  nullable = False),
           Column('max_retry', SmallInteger,  nullable = False),
           Column('poll_delay', Float, nullable = False),
           # Coicide con el nombre_uc de la esquina donde esta instaldo
           # el UC.
           Column('nombre_co', String(40)),
           
           # Este tiempo ya no se usa
           ## Tiempor de poll entre micro y micro
           # Column('t_poll', Float(presicion = 5),  nullable = False),
           
           )

class CO(object):
    def __init__(self, ip_address, id_CO = None, hab = True, t_poll = 3, t_out = 0.250, max_retry = 3,
                 poll_delay = 0.05, nombre_co = None):
        self.ip_address = ip_address
        if id_CO:
            self.id_CO = id_CO
        else:
            # Si no nos pasan el ID, tomamos la parte más baja de la direccion IP
            # Esto puede fallar si existen dos concentradores con la misma direccion
            # ip
            self.id_CO = int(ip_address.split('.')[3])
        self.desc = desc
        self.hab = hab
        self.t_poll = t_poll
        self.t_out = t_out
        self.max_retry = max_retry
        self.poll_delay = poll_delay
        self.nombre_co = nombre_co
        
    def __unicode__(self):
        return u'<Concentrador %d %s>' % (self.id_CO, self.ip_address)
    
    
    def __eq__(self, other):
        if type(other) != type(self):
            return False
        if hasattr(other, 'id') and other.id == self.id:
            return True
        return False
    
    __str__ = __repr__ = __unicode__

#===============================================================================
# Unidad de control
#===============================================================================

tabla_uc = Table('UC', metadata,
           # Esta columna es por simplicidad para no tener que hacer
           # complicaciones en las foreneas de SV, EV, DI y AI.
           Column('id', Integer, primary_key = True),
           Column('co_id', None, ForeignKey('CO.id_CO'), primary_key = True),
           
           # ID en RS485, minimo 2 máximo 63
           Column('id_UC', Integer, primary_key = True),
           Column('zona', SmallInteger), # 1 - 63
           Column('can_movi', Smallinteger), # 0 - 9
           
           # Nombre de SMF sin extension
           Column('nombre_uc', String(40) ),
           # Decripcion, habilitado
           
           Column('hab', Boolean),
           )

class UC(object):
    def __init__(self, co, id_UC, desc = None, hab = True, template = None, 
                 cant_di = None, cant_ai = None):
        '''
        @param co: Concentrador o ID del concentrador
        @param id_UC: ID en RS485
        @param desc: Descripcion del controlador
        @param hab: Hablitado
        @param template: Template para los puertos
        '''
        if type(co) == CO:
            self.co_id = co.id
        else:
            self.co_id = co
            
        if id_UC < 2 or id_UC > 63:
            raise ValueError('La id_UC debe estar entre 2 y 63')
        self.id_UC = id_UC
        self.desc = desc
        self.hab = hab
        
    def __unicode__(self):
        return u'<Unidad de Control %s %s>' % (self.id_UC, self.co)

    __str__ = __repr__ = __unicode__



# 
# ti_mov 0, subti_mov 0 = 3 luces
# ti_mov 0, subti_mov 1 = 2 luces derecha
# ti_mov 0, subti_mov 2 = 2 luces izquierda
# ti_mov 1, subti_mov 0 = 2 peatonal
# Ver la tabla semaforo
# x , y es la pos. del semaforo en el view

# El subtipo le pertenece al aparto, un mismo movimiento puede alimentarlo
# ergo timov cte. pero el aparto puede ser distinto ergo subtimov distinto 


tabla_Semaforo = Table('Semaforo', metadata,
                       Column('id', Integer, primary_key = True),
                       Column('uc_id', None, ForeignKey('UC.id')),
                       Column('Esquina_Calles_id', None, ForeignKey('Esquina_Calles.id')),
                       Column('ti_mov', SmallInteger),
                       Column('subti_mov', SmallInteger),
                       Column('n_mov', SmallInteger), 
                       Column('x', Integer, default = -1),
                       Column('y', Integer, default = -1)
                       )

class Semaforo(object):
    pass

tabla_Esquina = Table('Esquina', metadata,
                      Column('id', Integer, primary_key = True ),
                      Column('uc_id', None, ForeignKey('UC.id')),
#                      Column('nombre', String(40)), # Nombre de la jerga
                      Column('x', Float, default = -1),
                      Column('y', Float, default = -1)
                      )

class Esquina(object):
    def __init__(self, uc_id, x, y):
        self.uc_id = uc_id
        self.x = x
        self.y = y
        


# Tipo calle 0 = Doble mano con bvd (boulevard)
# Tipo calle 1 = Doble mano sin bvd
# Tipo calle 2 = Una mano saliente
# Tipo calle 3 = Una mano entrante

tabla_Esquina_Calles = Table('Esquina_Calles', metadata,
                             Column('id', Integer, primary_key = True),
                             Column('esquina_id', None, ForeignKey('Esquina.id')),
                             Column('calle_id', None, ForeignKey('Calle.id')),
                             Column('angulo', SmallInteger),
                             Column('tipo_calle', SmallInteger),
                             Column('sentido', String(2))
                             )

class Esquina_Calles(object):
    pass

# Nombre de las calles para reducir el error de tipeo

tabla_Calle = Table('Calle', metadata,
                             Column('id', Integer, primary_key = True),
                             Column('nombre', String(40)),
                             )

class Calle(object):
    def __init__(self, nombre):
        self.nombre = nombre
    
    def __str__(self):
        return "Calle: %s" % self.nombre
    
    __unicode__ = __repr__ = __str__


tabla_SV = Table('SV', metadata, 
                 Column('id', Integer, primary_key = True),
                 Column('uc_id', None, ForeignKey('UC.id')),
                 Column('nro_sv', Integer),
                 Column('valor', SmallInteger),
                 
                 )

class SV(object):
    ''' Variable de sistema,
    El valor se inicializa en -1'''
    
    NOT_INITIALIZED = -1
    
    def __init__(self, uc, nro_sv, valor = NOT_INITIALIZED):
        if type(uc) == UC:
            self.uc_id = uc.id
        else:
            self.uc_id = uc
        self.nro_sv = nro_sv
        self.valor = valor
    
    def __str__(self):
        return "SV "
    __repr__ = __str__
    
    
tabla_DI = Table('DI', metadata,
                 Column('id', Integer, primary_key = True),
                 Column('uc_id', None, ForeignKey('UC.id')),
                 Column('nro_port', Integer),
                 Column('valor', SmallInteger)
                 )



class DI(object):
    ''' Digital Input,
    El valor se inicializa en -1'''
    
    NOT_INITIALIZED = -1
    
    def __init__(self, uc, nro_port, valor = NOT_INITIALIZED):
        if type(uc) == UC:
            self.uc_id = uc.id
        else:
            self.uc_id = uc
        self.nro_port = nro_port
        self.valor = valor
    
    def __str__(self):
        return "DI "
    __repr__ = __str__
    
    @validates('uc')
    def validar_uc(self, uc):
        pass



    
tabla_AI = Table('AI', metadata,
                 Column('id', Integer, primary_key = True),
                 Column('uc_id', None, ForeignKey('UC.id')),
                 Column('nro_port', Integer),
                 Column('valor', SmallInteger),
                 )

class AI(object):
    
    NOT_INITIALIZED = -1
    MAX_VALUE = 2 ** 10 # Presicion de 10 bits
    def __init__(self, uc, nro_port, valor = DI.NOT_INITIALIZED):
        if type(uc) == UC:
            self.uc_id = uc.id
        else:
            self.uc_id = uc
        self.nro_port = nro_port
        self.valor = valor


# Atencion:
# N : No atendido
# A : Atendido
# R : Reparado
# Al pasar de N a A, guardo la fecha y hora 
# pasar de A a R, guardo la fecha y hora.
# No permito volver de A a N ni de R a A o N.

tabla_EV = Table('EV', metadata, 
                     Column('id',Integer, primary_key = True),
                     Column('uc_id', None, ForeignKey('UC.id')),
                     
                     # Se toman del TUC (tipo, urgencia [prioridad], codigo)
                     Column('tipo', SmallInteger),
                     Column('prio', SmallInteger),
                     Column('codigo', SmallInteger),
                     
                     Column('nro_port', SmallInteger, nullable = False),
                     Column('nro_bit', SmallInteger, nullable = False,),
                     Column('estado_bit', SmallInteger, nullable = False),
                     Column('ts_bit', DateTime, nullable = False),
                     Column('ts_bit_ms', Integer, nullable = False, default = 0),
                     # n -> Nuevo
                     # o -> Atendido
                     # r -> Reparado
                     Column('atendido', String(1), server_default = 'n'),
                     Column('ts_a', DateTime),
                     Column('ts_r', DateTime),
                     )

class EV(object):
    def __init__(self, uc, nro_port, nro_bit, estado_bit, tipo, codigo, prio , ts_bit):
        if type(uc) == UC:
            self.uc_id = uc.id
        else:
            self.uc_id = uc
        self.nro_port = nro_port
        self.nro_bit = nro_bit
        self.estado_bit = estado_bit
        self.ts_bit = ts_bit
        self.ts_bit_ms = ts_bit.microsecond / 100
        # Nuevos campos del TUC
        self.tipo = tipo
        self.codigo = codigo
        self.prio = prio

# Tipo y codigo viene en el TUC
# TUC ahora es Tipo Urgencia (Prioridad) y Codigo
#
tabla_EV_Descripcion = Table('EV_Descripcion', metadata,
                             

                        Column('id', Integer, primary_key = True),
                        
                        # Tipo coincide con EV.tipo (entero de 0 a 3)
                        #Column('tipo', mysql.MSTinyInteger, nullable = False),
                        Column('tipo', SmallInteger, 
                               CheckConstraint('tipo>0'), 
                               nullable = False),
                        # Código coincide con EV.codigo (entero de 0 a 3) 
                        Column('codigo', SmallInteger, nullable = False), 
                        Column('descripcion', String(50), nullable = False),
                        
                        UniqueConstraint('tipo', 'codigo', name = 'codigo_tipo_unico'),
                        
                        )
class EV_Descripcion(object):
    def __init__(self, tipo, codigo, descripcion):
        self.tipo = tipo
        self.codigo = codigo
        self.descripcion = descripcion
        
#===============================================================================
# Mapeos
#===============================================================================
mapper(CO, tabla_co, properties = {
    'ucs': relation(UC, backref='co'),# cascade="all, delete, delete-orphan"),
})

mapper(UC, tabla_uc, properties = {
    'dis': relation(DI, backref='uc'),#, cascade="all, delete, delete-orphan"),
    'ais': relation(AI, backref='uc')#, cascade="all, delete, delete-orphan"),
    # TODO: EV y SV
})


mapper(Semaforo,tabla_Semaforo, {
    'esquina_calles': relation(Esquina_Calles, backref= 'semaforo'),
    'uc': relation(UC, backref='semaforos'),
})

mapper(Esquina, tabla_Esquina, {
    'ucs': relation(UC, backref='esquinas')
})

mapper(Esquina_Calles, tabla_Esquina_Calles, {
    'esquina': relation(Esquina, backref='esquina_calles')                            
})

mapper(Calle, tabla_Calle, {

})

mapper(SV, tabla_SV, properties = {
    #'uc': relation(UControl, backref='dis'),
})

mapper(DI, tabla_DI, properties = {
    #'uc': relation(UControl, backref='dis'),
})

mapper(AI, tabla_AI, properties = {

})

mapper(EV, tabla_EV, properties = {

})

mapper(EV_Descripcion, tabla_EV_Descripcion, properties = {
})

