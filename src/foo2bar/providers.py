"""
This module defines a metadata provider that saves whether a name occurs for the first time in a given scope.
"""

import libcst as cst
from libcst.metadata import BatchableMetadataProvider, ScopeProvider, Scope

class FirstAssignInScopeProvider(BatchableMetadataProvider):
    METADATA_DEPENDENCIES = (ScopeProvider, )
    
    def visit_Module(self, module: cst.Module) -> None:
        self._visited_names_in_scope = dict[Scope, set[cst.Name]]()
    
    def visit_AssignTarget_target(self, assign: cst.AssignTarget) -> None:
        self._visit_assign_target(assign.target)
        
    def visit_AnnAssign_target(self, ann_assign: cst.AnnAssign) -> None:
        self._visit_assign_target(ann_assign.target)
    
    def _visit_assign_target(self, name: cst.Name):
        scope = self.get_metadata(ScopeProvider, name, None)
        # add empty set if scope has not been visited yet
        self._visited_names_in_scope.setdefault(scope, set())
        visited_names = self._visited_names_in_scope[scope]
        self.set_metadata(name, name.value not in visited_names)
        visited_names.add(name.value)