'''
This file tests the DSL for changing attribute

 +----------------------+   +------------------------+ +--------------------+
 |   Formula            |+->| SVGElement             | | SVGScreen          |
 |----------------------||  |------------------------| |--------------------|
 | last_error           ||  | tag                    | | name               |
 | formula              ||  | fill                   | | file               |
 | target (FK)+----------+  | stroke                 | |                    |
 +----------------------+   | text                   | |                    |
                            | screen (FK)+------------>|                    |
                            +------------------------+ +--------------------+
'''
from django_fasttest import TestCase
from factories import (ProfileFactory, COMasterFactory, IEDFactory, DIFactory, AIFactory,
                       SVGScreenFactory, SVGElementFactory, FormulaFactory)
from apps.hmi.models import Formula
from bunch import bunchify


class BasicFormulaDSLTestCase(TestCase):
    def setUp(self):
        self.profile = ProfileFactory()
        self.co_master = COMasterFactory(profile=self.profile)
        self.ied = IEDFactory(co_master=self.co_master)

        self.di0 = DIFactory(ied=self.ied, port=0, bit=0, tag='E4DI00', value=0)
        self.ai0 = AIFactory(ied=self.ied, tag='E4AI00', value=0)

        self.screen = SVGScreenFactory(profile=self.profile, name='E4', prefix='E4')
        self.element = SVGElementFactory(screen=self.screen, tag='E4EG00',
                                         text='',
                                         fill=0,
                                         stroke=0)


class TestContext(BasicFormulaDSLTestCase):

    def setUp(self):
        super(TestContext, self).setUp()
        self.formula_fill = FormulaFactory(target=self.element,
                                           attribute='fill',
                                           formula='SI(di.E4DI00.value,1,2)')

    def test_formula_full_context(self):
        ctx = Formula.full_context()
        self.assertEqual(len(ctx.di), 1, "There should be only E4DI00 in DI context")
        self.assertEqual(len(ctx.ai), 1, "There should be only E4AI00 in AI context")
        self.assertEqual(len(ctx.eg), 1, "There should be only E4EG00 in EG context")

    def test_formula_get_related(self):
        related = self.formula_fill.get_related()
        self.assertIn('di', related)
        self.assertIn('E4DI00', related['di'])
        self.assertNotIn('ai', related)
        self.assertNotIn('eg', related)

    def test_formula_context(self):
        context = self.formula_fill.context()
        self.assertEqual(len(context.di), 1)
        self.assertIn('E4DI00', context['di'])
        self.assertFalse(context.ai)
        self.assertFalse(context.eg)

    def test_overrides_existing_value(self):
        context = {
            'di': {
                'E4DI00': {
                    'value': 0
                }
            }
        }
        context = bunchify(context)
        Formula._patch_context(context, {'di.E4DI00.value': 1})
        self.assertEqual(context.di.E4DI00.value, 1, "Context should be updted")

    def test_overrides_non_existing_tag(self):
        context = {
            'di': {
                'E4DI00': {
                    'value': 0
                }
            }
        }
        context = bunchify(context)
        Formula._patch_context(context, {'di.E4DI01.value': 1})
        self.assertEqual(context.di.E4DI00.value, 0)
        self.assertEqual(context.di.E4DI01.value, 1)


class TestDSLCaheIsDroppedAfterFormulaIsUpdated(BasicFormulaDSLTestCase):

    def setUp(self):
        super(TestDSLCaheIsDroppedAfterFormulaIsUpdated, self).setUp()
        self.formula = FormulaFactory(target=self.element, attribute='fill', formula='1')

    def test_cache_is_dropped(self):
        init_prepeared_formula = self.formula.prepeared_formula
        self.formula.formula = '2'
        self.formula.save()
        self.assertNotEqual(init_prepeared_formula, self.formula.prepeared_formula,
                            "Cache was not cleared")


class TestDSLOperations(BasicFormulaDSLTestCase):

    def setUp(self):
        super(TestDSLOperations, self).setUp()
        self.formula_IF = FormulaFactory(target=self.element,
                                         attribute='fill',
                                         formula='SI(di.E4DI00.value,1,2)')

    def test_operation_si(self):
        ok = self.formula_IF.evaluate()
        self.assertTrue(ok, "Formula %s did not validate" % self.formula_IF.formula)


