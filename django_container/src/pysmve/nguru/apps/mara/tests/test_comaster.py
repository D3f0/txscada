# encoding: utf-8

from django_fasttest import TestCase

from apps.mara.models import Profile, Event, Energy, DI, Action, ComEventKind
from protocols.constructs import MaraFrame
from construct import Container
from copy import copy
from itertools import izip
from contextlib import contextmanager
from datetime import datetime

# from pysmve.protocols.constructs.tests import *


class TestBaseCOMaster(TestCase):

    def createCoMaster(self, profile, ieds=1, di_ports=2, di_bis=16, ais=0):
        comaster = profile.comasters.create(ip_address='127.0.0.1')
        for offset in range(ieds):
            ied = comaster.ieds.create(offset=offset, rs485_address=offset + 1)
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
            self.assertEqual([1, ] * 8 + [2, ],
                             [sv[0] for sv in comaster.svs.values_list('value')])

    def test_process_frame_with_digital_events(self):
        events = [
            Container(evtype="DIGITAL", q=0,
                      addr485=1, port=0, bit=7, status=0,
                      # Timestamp bytes
                      timestamp=datetime.now()
                              ),
            Container(evtype="DIGITAL", q=0,
                      addr485=2, port=0, bit=6, status=0,
                      # Timestamp bytes
                      timestamp=datetime.now()
                              ),

        ]
        frame = self.buildFrame10(events=events)

        with self.tempComaster(self.profile, ieds=2, di_ports=1) as comaster:
            comaster.process_frame(frame)
            evs = Event.objects.filter(di__ied__co_master=comaster,
                                       di__ied__rs485_address=events[
                                           0].addr485,
                                       di__port=events[0].port,
                                       di__bit=events[0].bit)
            self.assertEqual(evs.count(), 1)
            evs = Event.objects.filter(di__ied__co_master=comaster,
                                       di__ied__rs485_address=events[
                                           1].addr485,
                                       di__port=events[1].port,
                                       di__bit=events[1].bit)
            self.assertEqual(evs.count(), 1)

    def test_process_frame_with_analog_events(self):
        events = [
            Container(evtype="ENERGY", q=0,
                      addr485=1,
                      idle=0, code=0,  # Energía de 15 minutos
                      hnn=0,
                      channel=0,
                      value=131583,
                      timestamp=datetime.now()
                      ),
        ]
        frame = self.buildFrame10(events=events)
        with self.tempComaster(self.profile, ieds=2, di_ports=1, ais=1) as comaster:
            comaster.process_frame(frame)

            self.assertEqual(Energy.objects.get().value, events[0].value)

    def test_process_frame_with_com_events(self):
        events = [
            Container(
            # 1 byte (TCD)
            evtype="COMSYS", q=0, addr485=1,
            # 2 byte
            code=0,
            motiv=0,
            timestamp=datetime(2012, 1, 1, 1, 1, 1, 50000)
            )
        ]

        EventText.objects.create(idtextoev2=1, text="Com1", value=1)
        EventText.objects.create(idtextoev2=2, text="Com2", value=1)
        #ComEventKind.objects.create(texto_2=1, code)
        frame = self.buildFrame10(events=events)
        with self.tempComaster(self.profile, ieds=1, di_ports=1) as comaster:
            comaster.process_frame(frame)
            self.assertEqual(comaster.ieds.get().comevent_set.count(), 1)
            event = comaster.ieds.get().comevent_set.get()
            print eventp

class TestEventText2(TestBaseCOMaster):

    def setUp(self):
        self.profile = Profile.objects.create(name='test')

    def test_process_frame_with_digital_events(self):
        events = [
            Container(evtype="DIGITAL", q=0,
                      addr485=1, port=0, bit=7, status=0,
                      # Timestamp bytes
                      timestamp=datetime.now()
                              ),
        ]
        frame = self.buildFrame10(events=events)

        with self.tempComaster(self.profile, ieds=1, di_ports=1) as comaster:
            DI.objects.update(idtextoev2=0, description="Interruptor", )
            EventKind.objects.create(text="Cerrado", idtextoev2=0, value=0)
            comaster.process_frame(frame)
            evs = Event.objects.filter(di__ied__co_master=comaster,
                                       di__ied__rs485_address=events[
                                           0].addr485,
                                       di__port=events[0].port,
                                       di__bit=events[0].bit)
            self.assertEqual(unicode(evs.get()), "Interruptor Cerrado")


class TestPesoAccion(TestCase):

    def test_peso_accion(self):
        for i in range(8):
            Action.objects.create(bit=i,
                                  descripcion='Accion bit %d' % i,
                                  script='',
                                  argumentos='')

        def pks(objs):
            [obj.pk for obj in objs]



        self.assertEqual(
                        pks(Action.get_actions_for_peso(3)),
                        pks(Action.objects.filter(bit__in = [1,2]))
                        )
