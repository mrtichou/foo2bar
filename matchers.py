"""
This module describes which statements we would like to isolate before replacing them.

The global_statement_matcher is a matcher that matches all global statements that contain an assignment.
Out of these statements, we are interested in the first occurence of a variable name in a given scope.
From this first occurence, we would like to save the name of the variable, the type of the variable if it is explicitly annotated, and the value assigned to the variable.
In addition, we would like to save the trailing line comment associated with the assignment.

However, if the trailing line comment contains the phrase "no param", the full statement will be ignored.
"""

import re
from libcst import matchers as m, metadata
from providers import FirstAssignInScopeProvider

assign_name = m.Name(
    # Save the name of the variable
    value=m.SaveMatchedNode(m.DoNotCare(), "name"),
    # We care only about first occurence of a variable name in a given scope
    metadata=m.MatchMetadata(FirstAssignInScopeProvider, True),
)

# Save the type of the variable when explicitly annotated
assign_type = m.Annotation(annotation=m.SaveMatchedNode(m.DoNotCare(), "annotation"))

# Save the value node assigned to the variable to replace it later
assign_value = m.SaveMatchedNode(m.DoNotCare(), "value")

# A comment containing "no param" should not be saved
no_param = m.MatchRegex(re.compile(r".*no param.*", re.IGNORECASE))
# Save the comment if it does not contain "no param"
comment = m.Comment(value=m.SaveMatchedNode(m.DoesNotMatch(no_param), "comment"))
# If no comment is present, save None
no_comment = m.SaveMatchedNode(None, "comment")

# Match an assignment statement, be it annotated or not
assign_matcher = m.Assign(
    targets=[m.AssignTarget(target=assign_name)], value=assign_value
)
ann_assign_matcher = m.AnnAssign(
    target=assign_name, annotation=assign_type, value=assign_value
)

GLOBAL_SCOPE_NAME = ""


class UnnamedScopeError(ValueError):
    pass


def resolve_scope_name(scope: metadata.Scope) -> str:
    """Resolve scope path as a dot-separated chain of child scope names.
    
    This function differs from what `libcst.metadata.QualifiedNameProvider` can provide \
        since it omits `<local>` scopes, and raises an exception when 
    
    Example:
        While analyzing the scope metadata of following module:
        ```python
        class Foo:
            def bar(self):
                def baz():
                    bat = 5
        ```
        resolving the scope name of `baz` returns `"Foo.bar.baz"`
    
    Args:
        scope (metadata.Scope): The libcst.metadata.Scope object to be resolved.
        
    Raises:
        UnnamedScopeError: The provided scope or one of its parent scopes is not named, e.g. `lambda` function scopes.

    Returns:
        str: A dot-separated string chaining all scope names up from the global scope. 
    """

    def _resolve_scope_name(scope: metadata.Scope, children: str = "") -> str:
        if isinstance(scope, metadata.GlobalScope):
            return children
        elif getattr(scope, "name", None) is None:
            raise UnnamedScopeError(
                f"Cannot resolve name for unnamed scope: '{scope._name_prefix}'"
            )
        else:
            if not children:
                new_children = scope.name
            else:
                new_children = f"{scope.name}.{children}"
            return _resolve_scope_name(scope.parent, new_children)

    return _resolve_scope_name(scope)


def build_scoped_statement_matcher(scope_name: str) -> m.SimpleStatementLine:
    """Generate a matcher that extracts information from assignements in a given scope.

    Args:
        scope_name (str): Dot-separated path of the scope to inspect, like `"Foo.bar.baz"`. Set to `""` for inspecting global scope.

    Returns:
        m.SimpleStatementLine: A `libcst.matchers.Matcher` object matching the first tima a variable is assigned in a scope, \
            and extracting its name, the assigned value, the type annotation and the trailing comment.  
    """

    def scope_matcher(scope: metadata.Scope):
        try:
            return resolve_scope_name(scope) == scope_name
        except UnnamedScopeError:
            return False

    return m.SimpleStatementLine(
        metadata=m.MatchMetadataIfTrue(
            metadata.ScopeProvider,
            scope_matcher,
        ),
        body=[m.OneOf(assign_matcher, ann_assign_matcher)],
        trailing_whitespace=m.OneOf(
            m.TrailingWhitespace(comment=comment),
            m.TrailingWhitespace(comment=no_comment),
        ),
    )


# Match a global statement containing an assignment
global_statement_matcher = build_scoped_statement_matcher(GLOBAL_SCOPE_NAME)
