
from typing import Any, Mapping

import libcst as cst
from libcst import matchers as m, metadata

from .matchers import statement_matcher
from .providers import FirstAssignInScopeProvider

class Substitutor(m.MatcherDecoratableTransformer):
    METADATA_DEPENDENCIES = (metadata.ScopeProvider, FirstAssignInScopeProvider)
    
    def __init__(self, mapping: dict[str, str], scope: metadata.Scope = None) -> None:
        super().__init__()
        self.scope = scope
        self.mapping = mapping
        self._check_if_values_are_strings()
    
    def retrieve_non_substituted(self):
        return {k: v for k, v in self.mapping.items() if k in self._to_substitute}
    
    def visit_Module(self, node: cst.Module) -> bool:
        self._to_substitute = set(self.mapping.keys())
    
    @classmethod
    def from_repr(cls, typed_mapping: Mapping[str, Any], scope: metadata.Scope = None) -> "Substitutor":
        return cls({k:repr(v) for k, v in typed_mapping.items()}, scope)
    
    def _check_if_values_are_strings(self):
        for v in self.mapping.values():
            if not isinstance(v, str):
                raise ValueError(f"All values in the mapping must be strings. Got {v} instead. Maybe have a look at the `from_repr` method.")
    
    def _matches_scope(self, node: cst.CSTNode):
        if self.scope is None:
            return True
        scope = self.get_metadata(metadata.ScopeProvider, node)
        return scope == self.scope
    
    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> bool:
        self._current_data = m.extract(node, statement_matcher, metadata_resolver=self)
        return self._current_data is not None and self._matches_scope(node) # stop traversal if did not match

    def _leave_generic_assign(self, original_node: cst.Expr, updated_node: cst.Expr):
        current_name = self._current_data["name"]
        if current_name in self.mapping:
            self._to_substitute.discard(current_name)
            return updated_node.with_changes(value=cst.parse_expression(self.mapping[current_name]))
        return updated_node

    @m.call_if_inside(statement_matcher)
    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.Assign:
        return self._leave_generic_assign(original_node, updated_node)
    
    @m.call_if_inside(statement_matcher)
    def leave_AnnAssign(self, original_node: cst.AnnAssign, updated_node: cst.AnnAssign) -> cst.AnnAssign:
        return self._leave_generic_assign(original_node, updated_node)