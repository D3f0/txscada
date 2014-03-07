from django.test import SimpleTestCase
from apps.mara.utils import build_filter_funcs


class TestUtils(SimpleTestCase):

    def test_build_filter_funcs_with_no_function(self):

        generated_func = build_filter_funcs(None)
        self.assertTrue(generated_func(None), "Function should return True")
        self.assertTrue(generated_func(True), "Function should return True")
        self.assertTrue(generated_func(False), "Function should return True")
        self.assertTrue(generated_func(1), "Function should return True")
        self.assertTrue(generated_func({'a': 1}), "Function should return True")

    def test_build_filter_funcs_with_a_function(self):
        def test_func(v):
            return True

        generated_func = build_filter_funcs(test_func)
        self.assertEqual(generated_func, test_func, "When a just a function is returned"
                         "it should return it")

    def test_build_filter_funcs_with_many_functions(self):
        def f_false(v):
            return False

        def f_true(v):
            return True
        generated_func = build_filter_funcs([f_true, f_false, f_true])
        self.assertFalse(generated_func('x'), "One of the filters fail, so the filter"
                         "should fail")

        generated_func = build_filter_funcs([f_true, f_true])
        self.assertTrue(generated_func('x'), "No filters fail, so the filter should fail"
                        " succeed")
