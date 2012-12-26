# encoding: utf-8
'''
Generate intial dabtase entities based on mara XLS file
'''

from django.core.management.base import NoArgsCommand, CommandError
from optparse import make_option

DI_DESCRIPTION = '''Tension ALTA Bateria
Tension BAJA Bateria
Int Campo 1
Int Campo 2
Int Campo 3
Int Campo 4
Int PAT Campo 1
Int PAT Campo 2
Int PAT Campo 3
Int PAT Campo 4


Tension ALTA Bateria
Tension BAJA Bateria
Int Campo 1
Int Campo 2
Int Campo 3
Int Campo 4
Int PAT Campo 1
Int PAT Campo 2
Int PAT Campo 3
Int PAT Campo 4


Tension ALTA Bateria
Tension BAJA Bateria
Int Campo 1
Int Campo 2
Int Campo 3
Int Campo 4
Int PAT Campo 1
Int PAT Campo 2
Int PAT Campo 3
Int PAT Campo 4'''

DI_DESCRIPTION = DI_DESCRIPTION.split('\n')

EXCEL_CONFIG = (

                    (0, 6, 6, 2, 1),
                    (1, 6, 2, 4, 2),
                    (2, 6, 2, 4, 3),
                    (3, 6, 2, 4, 4),
                    (4, 6, 2, 4, 5),

)

PORT_WIDTH = 16 # 16 bits per port

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
                    make_option('-p', '--profile', help="Profile name",
                                dest='profile_name'),
                    make_option('-a', '--address', help="IP address",
                                action='append', default=[], dest='co_ips'),
                    make_option('-d', '--delete', help="Delete previous data",
                                action='store_true', default=False)
                 )
    help = '''Crea un COMaster con sus IED asociados en un perfil dado'''

    def handle_noargs(self, **options):
        from mara.models import Profile, Unit

        unidad, _ = Unit.objects.get_or_create(name='unidad')
        kv, _ = Unit.objects.get_or_create(name='kV')
        kw, _ = Unit.objects.get_or_create(name='kW')
        kwh, _ = Unit.objects.get_or_create(name='kWh')
        kva, _ = Unit.objects.get_or_create(name='kVA')
        kvah, _ = Unit.objects.get_or_create(name='kVAh')


        profile_name = options.get('profile_name')
        if not profile_name:
            raise CommandError("You need to provide a profile_name name")
        co_ips = options.get('co_ips')
        if not co_ips:
            raise CommandError("No address specified, use -a x.x.x.x to specify an IP")

        if options.get('delete'):
            try:
                Profile.objects.get(name__iexact=profile_name).delete()
            except Profile.DoesNotExist:
                pass
        profile, _created = Profile.objects.get_or_create(name=profile_name)
        for ip_address in co_ips:
            comaster = profile.comasters.create(ip_address=ip_address,
                                                enabled=True)

            for offset, canvarsys, candis, canais, rs485_address in EXCEL_CONFIG:
                # Create Comaster with Config
                ied = comaster.ieds.create(offset=offset,
                                           rs485_address=rs485_address,
                                           )
                # Var Sys are common to all
                # TODO: Better offset handling
                ied.sv_set.create(param='ComErrorL',
                                  width=8,
                                  description="Flag de errores",
                                  unit=unidad,
                                  offset=0)
                ied.sv_set.create(param='ComErrorH',
                                  width=8,
                                  description="Flag de errores",
                                  unit=unidad,
                                  offset=1)
                ied.sv_set.create(param='Sesgo',
                                  width=16,
                                  unit=unidad,
                                  offset=2)
                ied.sv_set.create(param='ClockError',
                                  width=8,
                                  unit=unidad,
                                  offset=4)
                ied.sv_set.create(param='UartError',
                                  width=8,
                                  unit=unidad,
                                  offset=5)

                # First IED is special, it holds more information

                if rs485_address == 1:
                    # AI
                    ied.ai_set.create(param='V',
                                      description='Tensión de Barra 33KV',
                                      offset=0,
                                      unit=kv)
                    # DIs
                    for port in range(candis / 2):
                        for bit in range(0, PORT_WIDTH):
                            n = (port * PORT_WIDTH) + bit
                            param = "D%.2d" % n
                            try:
                                desc = DI_DESCRIPTION[n]
                            except IndexError:
                                desc = None
                            ied.di_set.create(port=port,
                                              bit=bit,
                                              param=param,
                                              description=desc,
                                              offset=n / 8)

                else:
                    # Create others
                    # AI
                    ied.ai_set.create(param='P',
                                      description='Potencia Activa',
                                      offset=0,
                                      unit=kw)
                    ied.ai_set.create(param='Q',
                                      description='Potencia Reactiva',
                                      offset=2,
                                      unit=kva)
                    # Energy Points
                    ied.energypoint_set.create(
                                                channel=0,
                                                description=u"Energía Activa",
                                                param='Ea',
                                                unit=kwh,
                                                ke=0.025,
                                                divider=1,
                                                rel_tv=12,
                                                rel_ti=5,
                                                rel_33_13=2.5
                                                )
                    ied.energypoint_set.create(
                                                channel=1,
                                                description=u"Energía Reactiva",
                                                param='Er',
                                                unit=kvah,
                                                ke=0.025,
                                                divider=1,
                                                rel_tv=12,
                                                rel_ti=5,
                                                rel_33_13=2.5
                                                )

