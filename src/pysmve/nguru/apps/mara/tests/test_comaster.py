from django_fasttest import TestCase
from ..models import Profile
from pysmve.protocols.constructs import MaraFrame
from construct import Container
from copy import copy
from itertools import izip
from contextlib import contextmanager
from datetime import datetime

#from pysmve.protocols.constructs.tests import *

class TestBaseCOMaster(TestCase):

    def createCoMaster(self, profile, ieds=1, di_ports=2, di_bis=16, ais=0):
        comaster = profile.comasters.create(ip_address='127.0.0.1')
        for offset in range(ieds):
            ied = comaster.ieds.create(offset=offset, rs485_address=offset+1)
            for port_num in range(di_ports):
                for bit_num in range(di_bis):
                    ied.di_set.create(port=port_num, bit=bit_num)
            for ai_offset in range(ais):
                ied.ai_set.create(offset=ai_offset)

        return comaster

    @contextmanager
    def tempComaster(self, *args, **kwargs):
        comaster = self.createCoMaster(*args, **kwargs)
        yield comaster
        comaster.delete()

    BASE_CONTAINER = Container(
        sof=0xFE,
        length=0,
        dest=1,
        source=2,
        sequence=0x33,
        command=0x10,
        payload_10=Container(
            canvarsys=0,
            varsys=[],
            candis=0,
            dis=[],
            canais=0,
            ais=[],
            canevs=0,
            event=[]
        )
    )

    @classmethod
    def buildFrame10(cls, dis=[], ais=[], svs=[], events=[], through_construct=True):
        data = copy(cls.BASE_CONTAINER)
        data.payload_10.dis = dis
        data.payload_10.candis = len(dis) * 2 + 1
        data.payload_10.ais = ais
        data.payload_10.canais = len(ais) * 2 + 1
        data.payload_10.event = events
        data.payload_10.canevs = (len(events) * 10) + 1
        data.payload_10.varsys = svs
        data.payload_10.canvarsys = len(svs) * 2 + 1

        if through_construct:
            build = MaraFrame.build(data)
            data = MaraFrame.parse(build)
        return data


class TestCOMasterProperties(TestBaseCOMaster):

    def setUp(self):
        self.profile = Profile.objects.create(name='test')
        self.comaster = self.createCoMaster(profile=self.profile)



    def test_comaster_di_order(self):
        def generator(cant, ports, bits):
            for offset in range(cant):
                for port in range(ports):
                    for bit in range(bits):
                        yield offset, port, bit
        g = generator(1, 2, 16)
        for di, (offset, port, bit) in izip(self.comaster.dis, g):
            self.assertEqual(di.offset, offset)
            self.assertEqual(di.port, port)
            self.assertEqual(di.bit, bit)


class TestCOMasterFrame(TestBaseCOMaster):

    def setUp(self):
        self.profile = Profile.objects.create(name='test')
        self.comaster = self.createCoMaster(profile=self.profile)

    def test_process_frame_with_dis(self):
        # 16 bits integers are created by construct
        dis = [0xFFFF, ]
        frame = self.buildFrame10(dis=dis)
        with self.tempComaster(self.profile) as comaster:
            comaster.process_frame(frame)
            self.assertEqual(comaster.dis[0].value, 1)
            di_values = [di.value for di in comaster.dis[:16]]
            self.assertEqual([1 for _ in di_values], di_values)

    def test_process_frame_with_ais(self):
        ais = [10, 20]
        frame = self.buildFrame10(ais=ais)
        with self.tempComaster(self.profile, ais=2, ieds=1) as comaster:
            comaster.process_frame(frame)
            self.assertEqual(comaster.ais[0].value, 10)
            self.assertEqual(comaster.ais[1].value, 20)

    def test_process_frame_with_svs(self):
        with self.tempComaster(self.profile, ieds=1) as comaster:
            ied = comaster.ieds.get()
            ied.sv_set.create(offset=0, bit=0)
            ied.sv_set.create(offset=0, bit=1)
            ied.sv_set.create(offset=0, bit=2)
            ied.sv_set.create(offset=0, bit=3)
            ied.sv_set.create(offset=0, bit=4)
            ied.sv_set.create(offset=0, bit=5)
            ied.sv_set.create(offset=0, bit=6)
            ied.sv_set.create(offset=0, bit=7)
            ied.sv_set.create(offset=1, bit=0)

            frame = self.buildFrame10(svs=[0xFF, 0x2])
            comaster.process_frame(frame)
            self.assertEqual([1, ]* 8 + [2,],
                             [sv[0] for sv in comaster.svs.values_list('value')])

    def test_process_frame_with_events(self):
        event_data = Container(evtype="DIGITAL", q=0,
                               addr485=5, bit=0, port=3, status=0,
                               # Timestamp bytes
                               timestamp=datetime.now()
                               )
        frame = self.buildFrame10(events=[event_data])


