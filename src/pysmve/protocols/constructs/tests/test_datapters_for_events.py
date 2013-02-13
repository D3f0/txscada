from unittest import TestCase
from ..structs import Event, GenericEventTailAdapter, EnergyEventTailAdapter

class TestEventAdapters(TestCase):


    def event_can_be_build(self):
        event = Event.build()
