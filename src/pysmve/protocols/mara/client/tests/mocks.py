from mock import MagicMock


def COMasterMock():
    '''Creates a COMaster mock, should reassemble to the model one.
    We don't use factory boy here because we don't want to generate interdependencies
    with Django ORM code. This mock should have the bare minimum constants nedded
    for a protocol/clientfactory to work.
    '''
    comaster = MagicMock()
    comaster.sequence = None
    comaster.poll_interval = 5
    comaster.rs485_destination = 1
    comaster.rs485_source = 2
    return comaster
