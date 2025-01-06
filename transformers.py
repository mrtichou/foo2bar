
from typing import Any, Mapping
import libcst as cst
from libcst import matchers as m, metadata
from matchers import global_statement_matcher
from providers import FirstVisitInScopeProvider

class GlobalSubstitution(m.MatcherDecoratableTransformer):
    METADATA_DEPENDENCIES = (metadata.ScopeProvider, FirstVisitInScopeProvider)
    
    def __init__(self, mapping: Mapping[str, str]) -> None:
        super().__init__()
        self.mapping = mapping
        
    @classmethod
    def from_repr(cls, typed_mapping: Mapping[str, Any]) -> "GlobalSubstitution":
        return cls({k:repr(v) for k, v in typed_mapping.items()})
    
    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> None:
        self._current_data = m.extract(node, global_statement_matcher, metadata_resolver=self)

    def _leave_generic_assign(self, original_node: cst.Expr, updated_node: cst.Expr):
        if self._current_data["name"] in self.mapping:
            return updated_node.with_changes(value=cst.parse_expression(self.mapping[self._current_data["name"]]))
        return updated_node

    @m.call_if_inside(global_statement_matcher)
    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.Assign:
        return self._leave_generic_assign(original_node, updated_node)
    
    @m.call_if_inside(global_statement_matcher)
    def leave_AnnAssign(self, original_node: cst.AnnAssign, updated_node: cst.AnnAssign) -> cst.AnnAssign:
        return self._leave_generic_assign(original_node, updated_node)