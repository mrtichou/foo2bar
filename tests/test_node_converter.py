import unittest
import libcst as cst
from libcst import metadata

from ersatz.node_converter import (
    node_to_string,
    scope_name_is_resolvable,
    try_resolve_scope_name,
    resolve_scope_name,
    UnnamedScopeError
)

SAMPLE_STATEMENTS = [
    "pass",
    "1 + 1",
    "'a' + 'b'",
    "import os",
    "int",
    "x = 10",
    "y : int = 20",
    "def my_func(a, b, c):\n    return a + b + c",
]


SAMPLE_CODE = """
my_global_var = 10

def my_function():
    my_local_var = 20
    def my_nested_function():
        my_nested_var = 30

class MyClass:
    my_class_var = 40
    def my_method(self):
        my_instance_var = 50

my_list = [my_item for my_item in range(10)]

my_lambda = lambda my_lambda_var: my_lambda_var + 1
"""

SCOPE_NAMES = {
    "my_global_var": "",
    "my_local_var": "my_function",
    "my_nested_var": "my_function.my_nested_function",
    "my_class_var": "MyClass",
    "my_instance_var": "MyClass.my_method",
    "my_list": "",
    "my_item": None,
    "my_lambda": "",
    "my_lambda_var": None,
}

RESOLVABLE_SCOPES = {var: scope for var, scope in SCOPE_NAMES.items() if scope is not None}
UNRESOLVABLE_SCOPES = {var: scope for var, scope in SCOPE_NAMES.items() if scope is None}

class TestNodeConverter(unittest.TestCase):
    def setUp(self):
        self.wrapper = cst.MetadataWrapper(cst.parse_module(SAMPLE_CODE))
        self.scopes = self.wrapper.resolve(metadata.ScopeProvider)
        
    def get_variable_scope(self, name):
        return next(scope for node, scope in self.scopes.items() if isinstance(node, cst.Name) and node.value == name)

    def test_node_to_string(self):
        for node in SAMPLE_STATEMENTS:
            cst_node = cst.parse_statement(node)
            result = node_to_string(cst_node).rstrip("\n")
            self.assertEqual(result, node)

    def test_scope_name_is_resolvable(self):
        for name in RESOLVABLE_SCOPES:
            scope = self.get_variable_scope(name)
            self.assertTrue(scope_name_is_resolvable(scope))

        for name in UNRESOLVABLE_SCOPES:
            scope = self.get_variable_scope(name)
            self.assertFalse(scope_name_is_resolvable(scope))

    def test_try_resolve_scope_name(self):
        for var_name, scope_name in SCOPE_NAMES.items():
            scope = self.get_variable_scope(var_name)
            self.assertEqual(try_resolve_scope_name(scope), scope_name)

    def test_resolve_scope_name(self):
        for var_name, scope_name in RESOLVABLE_SCOPES.items():
            scope = self.get_variable_scope(var_name)
            self.assertEqual(resolve_scope_name(scope), scope_name)
            
        for var_name, scope_name in UNRESOLVABLE_SCOPES.items():            
            scope = self.get_variable_scope(var_name)
            with self.assertRaises(UnnamedScopeError):
                resolve_scope_name(scope)
        


if __name__ == "__main__":
    unittest.main()