from textwrap import dedent
import unittest
from pathlib import Path

import libcst as cst

from ersatz.wrapper import CodeWrapper, AssignementWrapper

class TestCodeWrapper(unittest.TestCase):
    def setUp(self):
        self.sample_code = dedent("""\
        x = 10  # comment
        x = x + 3 # overwrite value
        y: int = 20 # another comment
        z = 30
        class MyClass:
            a = 40
            def method(self):
                b = 50
                
        class IgnoreThemAll:
            s = 60  # no param
            t = 70  # NO PARAM
            u = 80  # No PaRaM
        """)
        self.wrapper = CodeWrapper(self.sample_code)

    def test_list_scope_names(self):
        expected_scopes = ["", "IgnoreThemAll", "MyClass", "MyClass.method"]
        self.assertEqual(sorted(self.wrapper.list_scope_names()), sorted(expected_scopes))

    def test_analyze_assigns_no_scope(self):
        assigns = self.wrapper.analyze_assigns()        
        self.assertEqual(len(assigns), 5)

    def test_analyze_assigns_no_param_comment(self):
        assigns = self.wrapper.analyze_assigns("IgnoreThemAll")
        self.assertEqual(len(assigns), 0)  

    def test_analyze_assigns_global_scope(self):
        assigns = self.wrapper.analyze_assigns("")
        self.assertEqual(len(assigns), 3)
        self.assertEqual(assigns[0].name, "x")
        self.assertEqual(assigns[1].name, "y")
        self.assertEqual(assigns[2].name, "z")
        
    def test_analyze_assigns_class_scope(self):
        assigns = self.wrapper.analyze_assigns("MyClass")
        self.assertEqual(len(assigns), 1)
        self.assertEqual(assigns[0].name, "a")

    def test_analyze_assigns_method_scope(self):
        assigns = self.wrapper.analyze_assigns("MyClass.method")
        self.assertEqual(len(assigns), 1)
        self.assertEqual(assigns[0].name, "b")

    def test_substitute_assign_values_global(self):
        self.wrapper.substitute_assign_values_global({"x": "100", "y": "200"})
        code = self.wrapper.code
        self.assertIn("x = 100", code)
        self.assertIn("y: int = 200 # another comment", code)
        self.assertIn("z = 30", code)

    def test_substitute_assign_values_class_scope(self):
        self.wrapper.substitute_assign_values({"a": "400"}, "MyClass")
        code = self.wrapper.code
        self.assertIn("a = 400", code)

    def test_substitute_assign_values_method_scope(self):
        self.wrapper.substitute_assign_values({"b": "500"}, "MyClass.method")
        code = self.wrapper.code
        self.assertIn("b = 500", code)


class TestAssignementWrapper(unittest.TestCase):
    def setUp(self):
        self.sample_code = dedent("""\
        x = 10  # comment
        y: int = 20  # another comment
        """)
        self.wrapper = CodeWrapper(self.sample_code)
        self.assigns = self.wrapper.analyze_assigns("")

    def test_name(self):
        self.assertEqual(self.assigns[0].name, "x")
        self.assertEqual(self.assigns[1].name, "y")

    def test_comment(self):
        self.assertEqual(self.assigns[0].comment, "# comment")
        self.assertEqual(self.assigns[1].comment, "# another comment")

    def test_scope_as_string(self):
        self.assertEqual(self.assigns[0].scope_as_string(), "")
        self.assertEqual(self.assigns[1].scope_as_string(), "")

    def test_value_as_string(self):
        self.assertEqual(self.assigns[0].value_as_string(), "10")
        self.assertEqual(self.assigns[1].value_as_string(), "20")

    def test_annotation_as_string(self):
        self.assertIsNone(self.assigns[0].annotation_as_string())
        self.assertEqual(self.assigns[1].annotation_as_string(), "int")


if __name__ == "__main__":
    unittest.main()