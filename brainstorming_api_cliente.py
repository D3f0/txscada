# Código en el cliente
# para notificaciones sobre cambios de CO y UC
channel = ChannelCreator(start_now = False)

channel.set_preferd_format('json')
channel.watch('/ucnet/co/*')

def event_listner(e):
    print e

channel.on_event(event_listner)

def co_creation_listener(e):
    print e

    if e.event_type == 'CREATE':
        print "Se creo un una nueva unidad de control %s " % e.event_payload
        

channel.on_event(co_update_listener, '/ucent/co/*/co/[1-9]')

chanel.start()

event_channel = ChannelCreator(filter_event_type = ['EVENT', 'DATA_POLL'])


def di_data_update(e):
    print "Se recibieron valores de DIs"
    event_sources = e.payload.keys()
    print event_sources
    
event_channel.watch('/ucnet/co/*/uc/*/di')
event_channel.on_update(di_data_update)



