
import re
from libcst import matchers as m, metadata
from providers import FirstVisitInScopeProvider

assign_name = m.Name(
    # Save the name of the variable
    value=m.SaveMatchedNode(m.DoNotCare(), "name"),
    # We care only about first occurence of a variable name in a given scope
    metadata=m.MatchMetadata(FirstVisitInScopeProvider, True)
)

# Save the type of the variable when explicitly annotated
assign_type = m.Annotation(annotation=m.Name(value=m.SaveMatchedNode(m.DoNotCare(), "dtype")))

# Save the value node assigned to the variable to replace it later
assign_value = m.SaveMatchedNode(m.DoNotCare(), "value")

# A comment containing "no param" should not be saved
no_param = m.MatchRegex(re.compile(r".*no param.*", re.IGNORECASE))
# Save the comment if it does not contain "no param"
comment = m.Comment(value=m.SaveMatchedNode(m.DoesNotMatch(no_param), "comment"))
# If no comment is present, save None
no_comment = m.SaveMatchedNode(None, "comment")

# Match an assignment statement, be it annotated or not
assign_matcher = m.Assign(targets=[m.AssignTarget(target=assign_name)], value=assign_value)
ann_assign_matcher = m.AnnAssign(target=assign_name, annotation=assign_type, value=assign_value)

# Match a global statement containing an assignment
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