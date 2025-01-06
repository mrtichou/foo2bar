import libcst as cst
from libcst.metadata import BatchableMetadataProvider, ScopeProvider, Scope

class FirstVisitInScopeProvider(BatchableMetadataProvider):
    METADATA_DEPENDENCIES = (ScopeProvider, )
    
    def visit_Module(self, module: cst.Module) -> None:
        self._visited_names_in_scope = dict[Scope, set[cst.Name]]()
        
    def visit_Name(self, name: cst.Name) -> None:
        scope = self.get_metadata(ScopeProvider, name, None)
        # add empty set if scope has not been visited yet
        self._visited_names_in_scope.setdefault(scope, set())
        visited_names = self._visited_names_in_scope[scope]
        self.set_metadata(name, name.value not in visited_names)
        visited_names.add(name.value)