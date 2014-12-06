# =======================================================================================
# POLL SETTINGS
# =======================================================================================

MARA_CONSTRUCT = 'protocols.constructs.MaraFrame'
POLL_PROTOCOL_FACTORY = 'protocols.mara.client.MaraPorotocolFactory'

POLL_FRAME_HANDLERS = (
    'apps.mara.handlers.DjangoORMMaraFrameHandler',
    # 'apps.mara.handlers.AMQPPublishHandler',
)
