import unittest

from libcst._exceptions import ParserSyntaxError

from foo2bar.evallib import (
    SafeEvaluationError,
    annotation_eval,
    safe_eval,
    safe_type_eval,
    try_safe_type_eval,
    try_annotation_eval,
    expression_contains_call
)


class TestEvalLib(unittest.TestCase):

    def test_annotation_eval(self):
        self.assertEqual(annotation_eval("int"), int)
        self.assertEqual(annotation_eval("list"), list)
        self.assertEqual(annotation_eval("list[int]"), list[int])
        with self.assertRaises(NameError):
            annotation_eval("xwdlkqj")
        with self.assertRaises(ValueError):
            annotation_eval("exit()")
        with self.assertRaises(ParserSyntaxError):
            annotation_eval("from pathlib import Path; print(Path('requirements.txt').read_text())")

    def test_safe_eval(self):
        self.assertEqual(safe_eval("1 + 1"), 2)
        self.assertEqual(safe_eval("'a' + 'b'"), 'ab')
        with self.assertRaises(SafeEvaluationError):
            safe_eval("import os")

    def test_safe_type_eval(self):
        self.assertEqual(safe_type_eval("1 + 1"), int)
        self.assertEqual(safe_type_eval("'a' + 'b'"), str)
        with self.assertRaises(SafeEvaluationError):
            safe_type_eval("import os")

    def test_try_safe_type_eval(self):
        self.assertEqual(try_safe_type_eval("1 + 1"), int)
        self.assertEqual(try_safe_type_eval("'a' + 'b'"), str)
        self.assertIsNone(try_safe_type_eval("import os"))

    def test_try_annotation_eval(self):
        self.assertEqual(try_annotation_eval("int"), int)
        self.assertEqual(try_annotation_eval("list"), list)
        self.assertEqual(try_annotation_eval("list[int]"), list[int])
        self.assertIsNone(try_annotation_eval("xwdlkqj"))
        self.assertIsNone(try_annotation_eval("exit()"))
        self.assertIsNone(try_annotation_eval("from pathlib import Path; print(Path('requirements.txt').read_text())"))

    def test_expression_contains_call(self):
        self.assertTrue(expression_contains_call("print('hello')"))
        self.assertFalse(expression_contains_call("1 + 1"))
        self.assertFalse(expression_contains_call("'a' + 'b'"))
        self.assertFalse(expression_contains_call("'a' + ('b' + 'c')"))


if __name__ == "__main__":
    unittest.main()