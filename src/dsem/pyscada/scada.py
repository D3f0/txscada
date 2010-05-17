#! /usr/bin/env python
# -*- encoding: utf-8 -*-


# Correccion de PATH
import sys
sys.path.append('..')
from model import * # Definiciones de la DB

from twisted.internet.protocol import ClientFactory
from twisted.internet.address import IPv4Address
from pyscada.protocol import PicnetProtocol #, PicnetProtocolFactory
from twisted.internet import threads, reactor, defer
#from twisted.internet.defer import Deferred
from twisted.python import log
from picnet import proto
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from picnet.proto import Paquete
from picnet.event import EventoCodigo as Evento
from twisted.internet.threads import deferToThread
from sqlalchemy import MetaData
from sqlalchemy import engine
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from itertools import izip, count
from copy import copy
# El fantástico módulo de configuración que ahora es parte del nuevo scada
from config import Config
from twisted.internet.defer import Deferred
from UserDict import UserDict

MAX_AI = 2 ** 10 - 1 # 10 bits en 1

class States:
    # Iniciado
    STARTED         = 0x00
    # Enviado requsisción de eventos
    READY           = 0x01
    STATE_REQ_SENT  = 0x02
    # Timeout
    TIMEOUT_ELAPSED = 0x03
    # Enviado peticion de más eventos
    MOREV_REQ_SENT  = 0x04
    # Cuando se completa, se espera
    REQ_ST_COMPLETE = 0x05

    # Output buffer tiene commandos para enviar
    COMMAND_QUEUED  = 0x06

    # Peticion de suspencion
    HANG_REQUEST    = 0x20
    HANGED          = 0x30
    # Cuando no tiene UCs asignadas
    LONELY          = 0x21
    
    # Cuando el CO termina
    HALTED          = 0x22

# Excepciones para mejor manejo de flujo

class NoUCException(Exception):
    pass
class NoCOException(Exception):
    pass
#===============================================================================
# PicnetSCADAProtocol
#===============================================================================
class PicnetSCADAProtocol(PicnetProtocol):
    # El factory debería ser seteado por el buildProtocol() del ClientFactory
    
    factory = None
    
    
    def __init__(self, co, session_class):
        '''
        Creación del buffer de envío.
        '''
        #log.msg('Creacion del buffer de envio para el protocolo')
        self._to_send_buffer = []
        self.co = co
        self.session_class = session_class

    
    def append_to_buffer(self, pkg):
        '''
        Encola un paquete en el buffer para su envío
        '''
        assert isinstance(pkg, Paquete)
        self._to_send_buffer.append(pkg)
        
            
    def connectionMade(self):
        # llamamos al padre...
        log.msg('Conexion Establecida')
        PicnetProtocol.connectionMade(self)
        
        self.seq = proto.MIN_SEQ # Iniciamos el número de secuencia
        
        self.scada_state = States.STARTED
        # Referencia al deferred para timeout
        self.timeout_defer = None
        self.tries = 0
        self.begin_poll()
    
    def begin_poll(self):
        '''
        Punto de reentrada cunando vuelve a comenzar el ciclo de scan
        '''
        # Reiniciar el indice
        self.current_uc = 0 
        #threads.deferToThread(self.read_CO_and_UC_config)
        d = Deferred()
        d.addCallback(self.read_CO_and_UC_config)
        d.callback(None)
        #self.read_CO_and_UC_config()
        #if self.state == States.HALTED:
        #    log.err('CO desactivado o inexistente')
        #    return
        #elif self.state == States.LONELY:
        #    log.err('CO sin UCs. Esperando UCs %.5f' % self.co.poll_delay)
        #    reactor.callLater(self.co.poll_delay, self.begin_poll) #@UndefinedVariable
        #    return
        #self.sendReqState()
        
    def read_CO_and_UC_config(self, *largs):
        '''
        Leer la configuración del concentrador desde la DB.
        '''
        #co_id = self.factory.concentrador.id_CO
        # Abrir una sesion contra la DB, buscamos el CO en la DB
        
        session = self.session_class()
        try:
            self.co = session.query(CO).filter( CO.id_CO == self.co.id_CO and CO.hab == True).first()
        
            if not self.co:
                raise NoCOException()
            
            self.ucs = session.query(UC).filter( UC.co_id == self.co.id_CO and 
                                                 UC.hab == True).group_by('id_UC').all()
            if not len(self.ucs):
                raise NoUCException()
            
        except NoCOException:
            self.state = States.HALTED
            log.err('CO deshabilitada o borrada')
        except NoUCException:
            self.state = States.LONELY
            log.err('CO sin UCs. Esperando UCs %.5f' % self.co.poll_delay)
            reactor.callLater(self.co.poll_delay, self.begin_poll) #@UndefinedVariable
        else:
            self.state = States.READY
            # Mapeo ID de RS485 a id de DB
            self.uc485_to_DBid = dict(map(lambda uc: (uc.id_UC, uc.id), self.ucs))
            # Lanzo la consulta en un deferred
            deferred = Deferred()
            deferred.addCallback(self.sendReqState)
            deferred.callback(None)
        finally:
            session.close()
        

    def dataReceived(self, data):
        # Recibimos los datos si no se venció el timeout
        if self.scada_state in (States.STATE_REQ_SENT,):
            PicnetProtocol.dataReceived(self, data)
    
    def next_seq(self):
        self.seq += 1
        if self.seq >= proto.MAX_SEQ:
            self.seq = proto.MIN_SEQ
        return self.seq
    
    def packageRecieved(self, pkg):
        # Cuando se completa un paquete
        try:
            self.timeout_defer.cancel()
        except Exception, e:
            log.msg('Error cancelando timeout')
        
        if self.scada_state == States.STATE_REQ_SENT:
            # Diferimos el gurdado en la DB, ya que es bloqueante...
            #reactor.callLater(0, self.saveToDB, pkg) #@UndefinedVariable
            threads.deferToThread(self.saveToDB, pkg)
            
            # Ingrementamos el número de secuencia
            self.next_seq()
            self.poll_next()
        
             

    def poll_next(self):
        ''' Poll del siguiente uc '''
        self.current_uc += 1
        # Termino la consulta
        cant_ucs = len(self.ucs)
        if self.current_uc >= cant_ucs:
            log.msg('<<< Ciclo de %d UCs terminado >>>' % cant_ucs) 
            self.scada_state = States.REQ_ST_COMPLETE
            # TODO: Hacer la diferencia
            reactor.callLater(self.co.poll_delay, self.begin_poll ) #@UndefinedVariable
        else:
            # Consulta al siguiente
            log.msg("Consultando nuevo micro en %.3f segs" % self.co.poll_delay)
            reactor.callLater(self.co.poll_delay, self.sendReqState) #@UndefinedVariable
    
    def save_system_varaibles(self, session, id_uc, sv_data):
        ''' Actualiza o crea variables de sistema '''
        for nro_sv, val_sv in enumerate(sv_data):
            try:
                sv = session.query(SV).filter((SV.nro_sv == nro_sv) & (SV.uc_id == id_uc)).one()
                sv.valor = val_sv
                session.add(sv)
                
            except NoResultFound:
                log.msg('Creando SV N°%d' % nro_sv)
                session.add(SV( id_uc, nro_sv, val_sv))
    
    def save_digital_inputs(self, session, id_uc, di_data):
        ''' Aactualiza o crea variables de estado '''
        # Las digitales son directas 
        for n_port, val_di in enumerate( di_data ):
            # Guardamos en la base
            try:
                # Buscamos la DI para actualizar su valor
                di = session.query(DI).filter((DI.nro_port == n_port) & (DI.uc_id == id_uc)).one()
                di.valor = val_di
                session.add(di)
                
            except NoResultFound:
                # TODO: Generar algun log acá.
                # Si no se encuentra, creamos el valor
                session.add(DI(id_uc, n_port, val_di))
    
    def save_analog_inputs(self, session, id_uc, ai_data):
        '''
        Los eventos utilizan dos bytes.
        '''
        num_ai = 0
        for pos_ai in range(0, len(ai_data), 2):
            val_ai = (ai_data[pos_ai + 1] + ai_data[pos_ai ] << 8) % AI.MAX_VALUE
            try:
                ai = session.query(AI).filter((AI.nro_port == num_ai) & (AI.uc_id == id_uc)).one()
                ai.valor = val_ai
                session.add(ai)
                
            except NoResultFound:
                session.add(AI(id_uc, num_ai, val_ai))
                
            except MultipleResultsFound:
                log.err("Multiples results found: %" % len(ai_data))
            num_ai += 1
    
    def save_events(self, session, id_uc, ev_data):
        # Eventos
        len_evs = len(ev_data)
        log.msg('Salvando %d eventos' % (len_evs / 8))
        # TODO: Ver si no me estoy comiendo un evento
        for _, start, stop in izip(count(0), xrange(0, len_evs, 8), xrange(8, len_evs + 1, 8)):
            data = ev_data[start:stop]
            #log.msg('Data: %s' % data)
            ev = Evento(data)
            
            session.add(EV(id_uc, ev.port, ev.bit, ev.event, ev.tipo, ev.codigo, ev.prio, ev.datetime(),
                           ))
        
    
    def saveToDB(self, pkg):
        '''
        Guarda un paquete en la base de datos. Al ser una operación bloqueante
        twisted nos obliga a usar un deferred.
        '''
        # Creamos la sesion a partir de la propiedad de clase
        session = self.session_class()
        payload = pkg.get_payload()
        #bkp_payload = copy(payload)
        
        # Buscamos el ID en la base de datos para el micro dado
        uc = session.query(UC).filter( CO.id_CO == self.co.id_CO and UC.id_UC == pkg.SRC).first()
                                  
        #UC_dbid = self.uc485_to_DBid[ pkg.SRC ]
        
        # Calculamos los offsets
        svs, dis, ais = [], [], []
        
        for vp in [svs, dis, ais]:
            length = payload.pop(0) - 1
            vp += payload[0: length]
            payload = payload[length:]
        # Lo que quedan son eventos
        evs = payload
        
        
        #self.save_system_varaibles(session, uc.id, svs)
        #self.save_digital_inputs(session, uc.id, dis)
        #self.save_analog_inputs(session, uc.id, ais)
        try:
            self.save_events(session, uc.id, evs)
        except AttributeError:
            # Este error se produce cuando el UC fue eliminado.
            log.err("Evento perdido.")
        # A la base !
        session.commit()
        session.close()
        self.notify_data(self.co.id_CO, pkg.SRC, svs, dis, ais, evs)
        
    def notify_data(self, co, uc, svs, dis, ais, evs):
        '''
        Este método esta para ser sobrecargado y actualizar la interfase.
        '''
        pass
    
    def uc(): #@NoSelf
        doc = """Apunta a la UC a la cual se esta poleando acutalmente""" #@UnusedVariable
       
        def fget(self):
            try:
                return self.ucs[ self.current_uc ]
            except IndexError:
                # No debería pasar nunca
                log.err('No existe el la UC n° %d en %s' % (self.current_uc, 
                                                            self.ucs))
                return None
        return locals()
       
    uc = property(**uc())
    
    def sendReqState(self, *largs):
        ''' Peticion de estados y eventos '''
        # Generacion del paquete, lo guardamos por si hay que retransmitir
        
        if self.state == States.HALTED or not self.transport.connected:
            log.msg('Deteniendo consulta')
            return
        # Hay un paquete que enviar
        if self._to_send_buffer:
            self.state = States.COMMAND_QUEUED
            pkg = self._to_send_buffer.pop(0)
            pkg['SEQ'] = self.seq
            log.msg('Comando: %s' % pkg )
            self.transport.write( pkg.octet_str() )
            
            self.next_seq()
            reactor.callLater( self.co.poll_delay, self.sendReqState ) #@UndefinedVariable
            log.msg('Envio del comando')
            return
        
        # TODO: Tomar de la confguracion del SCADA
        self.tries = 0
        self.current_pkg = Paquete.crear_estados_y_eventos(0x01, 
                                                           self.uc.id_UC,
                                                           self.seq)
        # Enviamos el paquete al medio
        self.transport.write(self.current_pkg.octet_str())
        # Cambio de estado
        self.scada_state = States.STATE_REQ_SENT
        # Preparamos el temeout
        log.msg('Poll ---> %.2d%.2d' % (self.co.id_CO, self.uc.id_UC))
        self.timeout_defer = reactor.callLater(self.co.t_out, self.timeoutElapsed) #@UndefinedVariable
    
    def resend(self):
        ''' Reenviamos el último paquete '''
        if self.state == States.HALTED:
            return
        # Reenviamos el paquete guardado
        self.transport.write(self.current_pkg.octet_str())
        # Cambio de estado... 
        self.scada_state = States.STATE_REQ_SENT
        # Seteo nuevamente el timeout
        self.timeout_defer = reactor.callLater(self.co.t_out, self.timeoutElapsed) #@UndefinedVariable
    
    def sendBuffer(self):
        pass
    
    def timeoutElapsed(self):
        ''' Cuando courre un timeout '''
        if self.state == States.HALTED:
            return
        else:
            print self.state
        
        log.msg("Timeout")
        self.scada_state = States.TIMEOUT_ELAPSED
        # Reinicializamos los buffer subyacentes
        self.reset()
        # Incrementamos el número de intentos
        self.tries += 1
        
        if self.tries >= self.co.max_retry:
            # Si la cantidad de intentos alcanzó el límite
            log.err('Cantidad máxima de reintentos excedratio para %s')
            try:
                session = self.session_class()
                uc = session.query(UC).filter( UC.id_UC == self.uc.id_UC).first()
                uc.hab = False
                session.commit()
                self.uc_state_change(self.co.id_CO)
            except Exception, e:
                log.err("-*-"*15)
                log.err('Error deshabilitando %s (Eliminada desde la GUI?) %s\n%s', 
                        self.uc, e)
                log.err("-*-"*15)
            self.poll_next()
        else:
            # Reenviamos en caso contrario
            self.resend()
    
    def uc_state_change(self, co):
        pass

    
    def connectionLost(self, reason):
        try:
            self.timeout_defer.cancel()
        except:
            pass
        
        self.state = States.HALTED
        # El SCADA pierde la referencia. Ahora es nuestra misión
        # ser comidos por el GC.
        self.factory.forget_client( self.co.ip_address )
        log.msg('Cierre de hilo')


#===============================================================================
# PicnetSCADAProtocolFactory
#===============================================================================
class PicnetSCADAProtocolFactory(ClientFactory):
    '''
    Construye instancias de prtocolo
    '''
    # Protocolo
    protocol = PicnetSCADAProtocol
    _proto_instance = None
    def __init__(self, co, db_session_class):
        self.co = co
        self.Session = db_session_class
        
    
    def proto_instance(): #@NoSelf
        doc = """Solo una instancia del protocolo""" #@UnusedVariable
        def fget(self):
            if not self._proto_instance:
                self._proto_instance = self.protocol(self.co, self.Session)
                # Seteamos el factory, esto es importante, porque puede haber muchas 
                # instancias de protocol, pero solo un Factory por vida de concentrador
                # en el sacada.
                self._proto_instance.factory = self
            return self._proto_instance
           
        return locals()
       
    proto_instance = property(**proto_instance())
        
    def startedConnecting(self, connector):
        log.msg('Iniciando conexion.')
    
    def buildProtocol(self, addr):
        log.msg('Conectado.')
        return self.proto_instance
        
    
    def clientConnectionLost(self, connector, reason):
        log.msg('%s' %
                # Solo mostramos info extra si estamos en modo verborragico
                reason.getErrorMessage())
    
    def clientConnectionFailed(self, connector, reason):
        log.msg('Falla la conexión. Razón: %s' % reason.getErrorMessage())
    
    def __str__(self):
        return "Factory"
    
    __repr__ = __str__

    
    
#===============================================================================
# SCADAEngine
#===============================================================================
class SCADAEngine(object):
    '''
    Esta clase constituye un facade entre la aplicación CLI y/o GUI con el 
    motor Scada
    '''
    
    __tcp_port = None
    __metadata = None
    __db_engine = None
    __id_rs485 = None
    # Clase por defecto
    __factory_class = PicnetSCADAProtocolFactory
    __protocol_class = PicnetSCADAProtocol
    __verbosity = 1
    
    __clients = {}
    
    ''' Usar esta prpiedad antes del start '''
    after_connection = defer.Deferred()
    
    connection_defer = defer.Deferred()
    
    clients = property(lambda s: s.__clients, doc="Mapeo de Concentradores -> ClientFacoty")
    
    
    def protocol(): #@NoSelf
        doc = """Rereferencia a la clase del prtocolo, debe ser una subclase de PicnetProtocol""" #@UnusedVariable
       
        def fget(self):
            return self.__protocol
           
        def fset(self, value):
            if not issubclass(value, PicnetProtocol):
                raise ValueError("La clase del protocolo debe ser subclase de PicnetProtocol")  
            self.__protocol = value
           
        def fdel(self):
            del self._protocol
           
        return locals()
       
    protocol = property(**protocol())
    
    def __set_verbosity(self, verbosity):
        if verbosity < 0 or verbosity > 3:
            raise ValueError("No se puede setear un nivel de verborragia")
        self.__verbosity = verbosity
        
    verbosity = property(lambda s: s.__verbosity, __set_verbosity, doc="Nivel de verborragia")
    
    
    def tcp_port(): #@NoSelf
        doc = """Docstring""" #@UnusedVariable
       
        def fget(self):
            return self.__tcp_port
           
        def fset(self, value):
            if value < 1 or value > 65535:
                raise ValueError('El puerto no esta en el rango')
            self.__tcp_port = value
           
        return locals()
       
    tcp_port = property(**tcp_port())
    
    def metadata(): #@NoSelf
        doc = """SqlAlchemy Metadata (definicion de tablas)""" #@UnusedVariable
       
        def fget(self):
            return self.__metadata
           
        def fset(self, value):
            if not isinstance(value, MetaData):
                raise ValueError('Metadata debe ser una instancia de metadata')
            self.__metadata = value
           
        return locals()
       
    metadata = property(**metadata())
    
    
    
    def __set_factory_class(self, klass):
        if not issubclass(klass, ClientFactory):
            raise ValueError("La clase %s no es subclase de ClientFactory" % klass)
        self.__factory_class = klass
        
    factory = property(lambda s: s.__factory_class, __set_factory_class, doc="Factory")
    
    def __set_id_rs485(self, id):
        if id < 0 or id > 63:
            raise ValueError('ID incorrecto')
        self.__id_rs485 = id
        
    id_rs485 = property(lambda s: s.__id_rs485, __set_id_rs485, doc="ID del centro de control")
    
    

    def set_db_engine(self, value):
        self.__db_engine = value
    
    db_engine = property(lambda s: s.__db_engine, set_db_engine, doc= "Db_engine's Docstring")
    
    def __str__(self):
        try:
            return "<SCADAEngine Protocol: %s DB: %s>" % (self.prtocol, 
                                                                       self.db_engine)
        except:
            return "<SCADA Engine>"
    
    
    def __init__(self):
        ''' Constructor '''
        self.started = False
        self.client_facotries = []
        self.create_connection_chain()
            
    #connection_established = False
    
    def create_connection_chain(self):
        self.connection_defer.addCallback(self.read_db)
        self.connection_defer.addErrback(self.db_fail)
        self.connection_defer.addCallback(self.retrieve_cos).addErrback(self.cos_fail)
    
    def fire_connection_chain(self):
        self.connection_defer.callback(None)
    
    def start(self, *largs):
        ''' Este método inicia el scada'''
        if not self.started:
            log.msg('SCADA: Start')
            self.started = True
            reactor.callLater(0, self.fire_connection_chain)
                        
            
    def stop(self, *largs):
        ''' Detiene el scada '''
        if not self.started:
            log.msg('Scada detenido, no se puede detener')
        else:
            pass
            # TODO: Ver la detencion del scada de manera correcta.
#            for co, cf in self.clients:
#                cf.looseConnection()
            
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def read_db(self, foo_arg):
        self.engine = create_engine(self.db_engine, echo=(self.verbosity > 1))
        
        self.connection = self.engine.connect()
        # Seteamos el engine a la base de deatos
        self.metadata.bind = self.engine
        
        try:
            log.msg('Conectando con la Base de Datos')
            self.metadata.create_all(self.engine)
        except NotImplementedError:
            # Por alugna razon no funciona del todo bien esto
            pass
        # Dejamos la clase session
        self.Session = sessionmaker( bind = self.engine )
        # Retornamos la sesion inicial al deferred inicial
        return self.Session()
    
    def db_fail(self, exc):
        '''
        Para sobrecargar
        '''
        log.msg("Error en la conexion con la DB: %s" % exc.getErrorMessage())
    
    def cos_fail(self,exc):
        ''' Error en los concentradores '''
        log.err("Error en los concentradores: %s" % exc)
    
    def retrieve_cos(self, session):
        '''
        Por cada CO genera.
        '''
        log.msg('DB OK.')
        cos =  session.query(CO)
        cos_hab = cos.filter(CO.hab == True)
        log.msg('Encontrados %d/%d' % (cos_hab.count(), cos.count()) )
        for c in cos_hab.all():
            # Le pasamos al protocolo la clase generadora de sesiones y el concentrador
            cf = self.factory(c, self.Session)
            log.msg("Estableciendo conexion con %s:%s" % (c.ip_address, self.tcp_port))
            reactor.connectTCP(c.ip_address, self.tcp_port, cf)
            self.clients[c] = cf
        # Una vez que se generaron todos los clientes
        log.msg('Conexiones iniciadas...')
        return self.clients



class ScadaClientFacotry(ClientFactory, object):
    ''' 
    En vez de tener muchos client factory, creamos uno solo y modificamos
    el buildProtocol para instanciar diferentes prtocolos segun el concentrador
    del que se trate.
    '''
    # Protocolo
    protocol = PicnetSCADAProtocol
    
    class STATES:
        '''
        '''
        STOPPED         = 0x01
        STARTING        = 0x02
        STARTED         = 0x03
        STOPPING        = 0x04
    
    def __init__(self, cfg = None):
        '''
        @param cfg: Una instancia de config.Config o una mapping.
        '''
        # Creamos la instancia por defecto de configuración
        self.cfg = Config()
        # por defecto es verborrágico
        self.cfg.verbosity = 1
        
        if cfg:
            for k, v in cfg.iteritems(): # los Config y los dicts son "hashes"
                self.cfg[k] = v
                
        # Clinetes, se generan en el build protocol
        self.clients = {}
        
        self._state = self.STATES.STOPPED

    _session_class = None
    def session_class(): #@NoSelf
        doc = "Clase que genera la sessiones con la DB"
        def fget(self):
            if not self._session_class:
                self._session_class = sessionmaker(bind = self.db_engine)
            return self._session_class
        return locals()
    session_class = property(**session_class())
    
    def state(): #@NoSelf
        doc = """Estado del motor""" #@UnusedVariable
       
        def fget(self):
            return self._state
           
        def fset(self, value):
            self._state = value
        return locals()
       
    state = property(**state())
    
    _metadata = None
    def metadata(): #@NoSelf
        doc = """Definición de las tablas de la DB en SQLAlchemy""" #@UnusedVariable
       
        def fget(self):
            return self._metadata
           
        def fset(self, value):
            assert type(value) is MetaData, "No es metadata valido para SQLAlchemy"
            if self.db_engine and not value.bind:
                value.bind = self.db_engine
            self._metadata = value
            
        return locals()
       
    metadata = property(**metadata())
    
    _db_engine = None
    def db_engine(): #@NoSelf
        doc = """Motor de base de datos
        Si se seteó la metadata, automáticamente se asocia el engine con la 
        metadata de manera de tener preparada la sesión.
        """ #@UnusedVariable
       
        def fget(self):
            return self._db_engine
           
        def fset(self, value):
            if type(value) == engine.base.Engine:
                # Suponemos que está conectada
                self._db_engine = value
                
            elif type(value) in (unicode, str):
                
                self._db_engine = create_engine(value, echo=self.cfg.verbosity)
                
                self._db_engine.connect()
                if self.metadata and not self.metadata.bind:
                    self.metadata.bind = self._db_engine
            else:
                raise AssertionError('No se reconoce %s como un engine para SQLAlchemy' % value)
        return locals()
       
    db_engine = property(**db_engine())
    
    def tcp_port(): #@NoSelf
        doc = """Puerto tcp""" #@UnusedVariable
       
        def fget(self):
            return self._tcp_port
           
        def fset(self, value):
            assert value < 65535 and value > 1024, "Puerto invalido %d" % value
            self._tcp_port = value
        return locals()
       
    tcp_port = property(**tcp_port())
    
    def start(self, *largs):
        '''
        Arrancar el motor.
        '''
        if self.state == self.STATES.STOPPED:
            self.state = self.STATES.STARTING
            reactor.callLater(0, self.startup) #@UndefinedVariable
        else:
            log.msg('Scada no detenido. NO se inicia: %d' % self.state)
            
    def startup(self, *largs):
        '''
        Startup
        '''
        log.msg('Iniciando scada')
        self.connection_deferred = Deferred()
        session = self.session_class()  # Sessión con la DB
        self.connection_deferred.addCallback(self.read_or_update_CO_from_DB)    # Lectura de la DB
        self.connection_deferred.callback(session)
            
    def stop(self, *largs):
        '''
        Detener el motor. La detención no es instantanea. Los
        sockets permanecen abiertos.
        '''
        if self.state in [self.STATES.STARTED, self.STATES.STARTING, ]:
            self.state = self.STATES.STOPPING
            log.msg('Intentando detener')
            for c in self.clients.values():
                c.transport.loseConnection()
                
    
    def forget_client(self, ip):
        if ip in self.clients:
            self.clients.pop(ip)
        if not self.clients:
            self.state = self.STATES.STOPPED
            reactor.callLater(0, self.stopped) #@UndefinedVariable
            
    
    def kill(self):
        '''
        Detener el scada cerrando todos los sockets.
        '''
        pass
    
    def stopped(self):
        ''' Hook '''
        log.msg('Sacada detenido')
    
    def started(self):
        ''' Hook '''
        log.msg('Arranque de SCADA completado')
    
    # Temporal para los concentradores que se están conectando
    _connecting_cos_by_ip = {}
    def read_or_update_CO_from_DB(self, session):
        ''' Lee los concentradores de la Base de datos y lanza un deferred para
            conectarse con cada uno de ellos '''
        cos =  session.query(CO)
        cos_hab = cos.filter(CO.hab == True)
        log.msg('Encontrados %d/%d' % (cos_hab.count(), cos.count()) )
        for co in cos_hab.all():
            ip = co.ip_address
            # Ni conectado, ni conectando...
            if not ip  in self.clients and not ip in self._connecting_cos_by_ip:
                self._connecting_cos_by_ip[co.ip_address] = co
                reactor.connectTCP(co.ip_address, self.tcp_port, self) #@UndefinedVariable
            else:
                log.msg('Ya conectado con %s' % ip)
        self.state = self.STATES.STARTED
        reactor.callLater(0, self.started) #@UndefinedVariable
    
    def buildProtocol(self, addr):
        co = self._connecting_cos_by_ip.pop( addr.host )
        protocol = self.protocol(co, self.session_class)
        protocol.factory = self # Referencia cruzada
        self.clients[ addr.host ] = protocol
        return protocol


    def clientConnectionFailed(self, connector, reason):
        #return ClientFactory.clientConnectionFailed(self, connector, reason)
        log.msg('Conexion rechazada con %s' % connector )
        #d = Deferred()
        #d.addCallback(self.startup)
        #d.callback(None)

    def clientConnectionLost(self, connector, reason):
        log.msg('Perdida de conexion con %s' % connector)
        #return ClientFactory.clientConnectionLost(self, connector, reason)
    
    def connected(): # @NoSelf
        doc = "Indicador de conexion"
        def fget(self):
            return self.state == self.STATES.STARTED
        return locals()
    connected = property(**connected())
        

#===============================================================================
# main
#===============================================================================
def main(argv = sys.argv):
    '''
    Scada nivel consola.
    '''
    
#    parser = ScadaConfigParser(usage = '', version = '0.2', 
#                               description = 'Modulo scada', 
#                               prog='scada', 
#                               epilog = 'Motor scada')
#    options, args = parser.parse_args(argv[1:])
#    
    log.startLogging(sys.stdout, setStdout = False)
    
    # Creamos una instancia de Scada
    #scada = SCADAEngine()
    scada = ScadaClientFacotry()
    # Puerto TCP 
    scada.tcp_port = 9761
    # Descripcion de la base de datos
    scada.metadata = metadata
    # Verborragia minima
    scada.verbosity = 1
    # El concentrador tiene DI = 1
    scada.id_rs485 = 1
    
    scada.db_engine = 'mysql://dsem:passmenot@localhost:3306/dsem'
    
    
    log.msg("Inicnando scada", scada)
    
    #scada.connection_defer.addCallback(lambda c: log.msg("Clientes %s" % c))
    scada.start()
    reactor.callLater(5, scada.stop)
    reactor.callLater(10, lambda x: log.msg('Reactivando') or scada.start(), None)
    reactor.run()

if __name__ == '__main__':
    sys.exit(main())