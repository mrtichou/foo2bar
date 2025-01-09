import unittest
from textwrap import dedent

import libcst as cst
from libcst import matchers as m, metadata

from fusible.matchers import statement_matcher


class TestMatchers(unittest.TestCase):
    @staticmethod
    def _wrap_code(code: str) -> metadata.MetadataWrapper:
        return metadata.MetadataWrapper(cst.parse_module(code))

    @classmethod
    def _extract_all(cls, code: str):
        return m.extractall(cls._wrap_code(code), statement_matcher)

    @classmethod
    def _findall(cls, code: str):
        return m.findall(cls._wrap_code(code), statement_matcher)

    def test_match_assignment(self):
        code = dedent(
            """\
        x = 10  # valid comment
        y : int = 20  # valid comment
        z = '''
        multi-line
        string
        ''' # another valid comment
        u = [1, 2, 3]  # noparam        
        """
        )
        matches = self._extract_all(code)
        self.assertTrue(matches)
        for match in matches:
            self.assertIn("name", match)
            self.assertIn("value", match)
            self.assertIn("comment", match)

    def test_ignore_no_param_comment(self):
        code_with_no_param = dedent(
            """\
        x = 10  # no param
        y = 20  # valid comment
        """
        )
        matches = self._extract_all(code_with_no_param)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "y")

    def test_annotated_assignment(self):
        matches = self._extract_all("x: int = 10")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "x")
        self.assertEqual(matches[0]["annotation"].value, "int")

    def test_no_comment(self):
        matches = self._extract_all("x = 10")
        self.assertEqual(len(matches), 1)
        self.assertIsNone(matches[0]["comment"])

    def test_inside_function_scope(self):
        code = dedent(
            """\
        def foo():
            x = 10  # inside function
        """
        )
        matches = self._extract_all(code)
        self.assertEqual(len(matches), 1)

    def test_inside_class_scope(self):
        code = dedent(
            """\
        class Foo:
            x = 10  # inside class
        """
        )
        matches = self._extract_all(code)
        self.assertEqual(len(matches), 1)


if __name__ == "__main__":
    unittest.main()
