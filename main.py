
import json
from pathlib import Path
import re

import libcst as cst
from libcst import parse_module, matchers as m, metadata

class FirstVisitInScopeProvider(metadata.BatchableMetadataProvider):
    METADATA_DEPENDENCIES = (metadata.ScopeProvider, )
    
    def visit_Module(self, module: cst.Module) -> None:
        self._visited_names_in_scope = dict[metadata.Scope, set[cst.Name]]()
        
    def visit_Name(self, name: cst.Name) -> None:
        scope = self.get_metadata(metadata.ScopeProvider, name, None)
        # add empty set if scope has not been visited yet
        self._visited_names_in_scope.setdefault(scope, set())
        visited_names = self._visited_names_in_scope[scope]
        self.set_metadata(name, name.value not in visited_names)
        visited_names.add(name.value)
            

assign_name = m.Name(
    value=m.SaveMatchedNode(m.DoNotCare(), "name"),
    metadata=m.MatchMetadata(FirstVisitInScopeProvider, True)
)
assign_type = m.Annotation(annotation=m.Name(value=m.SaveMatchedNode(m.DoNotCare(), "dtype")))
assign_value = m.SaveMatchedNode(m.DoNotCare(), "value")

# A comment containing "no param" should not be saved
no_param = m.MatchRegex(re.compile(r".*no param.*", re.IGNORECASE))
comment = m.Comment(value=m.SaveMatchedNode(m.DoesNotMatch(no_param), "comment"))
no_comment = m.SaveMatchedNode(None, "comment")

assign_matcher = m.Assign(targets=[m.AssignTarget(target=assign_name)], value=assign_value)
ann_assign_matcher = m.AnnAssign(target=assign_name, annotation=assign_type, value=assign_value)

global_statement_matcher = m.SimpleStatementLine(
        metadata=m.MatchMetadataIfTrue(
            metadata.ScopeProvider,
            lambda scope: isinstance(scope, metadata.GlobalScope),
        ),
        body=[m.OneOf(assign_matcher, ann_assign_matcher)],
        trailing_whitespace=m.OneOf(
            m.TrailingWhitespace(comment=comment),
            m.TrailingWhitespace(comment=no_comment), 
        )
    )




def main() -> None:
    file_path = Path("test_data/test_script.py")
    initial_code = file_path.read_text()
    
    initial_module = parse_module(initial_code)
    
    # print(initial_module)
    wrapper = metadata.MetadataWrapper(initial_module)
    
    global_statements = m.extractall(wrapper, global_statement_matcher)
    
    print(json.dumps(global_statements, indent=4, default=str))
    
    # print(dict(wrapper.resolve(FirstVisitInScopeProvider)))
    
if __name__ == "__main__":
    main()
    
    
    
