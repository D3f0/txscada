from unittest import TestCase
from construct import Embed, Enum, Struct, Byte, Switch


class TestEmbedingBranch(TestCase):

    def setUp(self):

        self.cons = Struct('foo',
            Enum(Byte("a_enum"),
                ALFA=1,
                BETA=2
                ),
                Switch('switch', lambda ctx: ctx.a_enum, {
                    'ALFA': Embed(Struct('struct_alfa', Byte('byte_alfa'))),
                    'BETA': Embed(Struct('struct_beta', Byte('byte_beta'))),
                })
            )

    def test_construct(self):
        contents = self.cons.parse('\x01\x03\xee\x33')
        self.assertIn('a_enum', contents)
        self.assertEqual(contents['a_enum'], 'ALFA')
        self.assertIn('byte_alfa', contents)


