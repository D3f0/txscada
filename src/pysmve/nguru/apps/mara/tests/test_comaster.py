from django_fasttest import TestCase
from ..models import Profile
from pysmve.protocols.constructs import MaraFrame
from construct import Container
from copy import copy

class BaseProfileTest(TestCase):

    def setUp(self):
        self.profile = Profile.objects.create(name='test')
        self.comaster = self.createCoMaster(profile=self.profile)


    def createCoMaster(self, profile, ieds=3, di_ports=1, di_bis=16):
        comaster = profile.comasters.create(ip_address='127.0.0.1')
        for offset in range(ieds):
            ied = comaster.ieds.create(offset=offset, rs485_address=offset+1)
            for port_num in range(di_ports):
                for bit_num in range(di_bis):
                    ied.di_set.create(port=port_num, bit=bit_num)
        return comaster


    BASE_CONTAINER = Container(
        sof=0xFE,
        length=0,
        dest=1,
        source=2,
        sequence=0x33,
        command=0x10,
        payload_10=Container(
            canvarsys=2,
            varsys=[33],
            candis=0,
            dis=[],
            canais=0,
            ais=[],
            canevs=11,
            event=[ ]
        )
    )

    def test_process_frame(self):
        data = copy(self.BASE_CONTAINER)
        data.payload_10.dis = [0xFF, ]
        self.comaster.process_frame(data.payload_10)
