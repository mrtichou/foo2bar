import libcst as cst
from libcst import metadata


class UnnamedScopeError(ValueError):
    pass


def node_to_string(node: cst.CSTNode) -> str:
    return cst.Module(body=[node]).code


def scope_name_is_resolvable(scope):
    try:
        resolve_scope_name(scope)
        return True
    except UnnamedScopeError:
        return False


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
    return _resolve_scope_name(scope)


def _resolve_scope_name(scope: metadata.Scope, children: str = "") -> str:
    """Recursive implementation of resolve_scope_name"""
    if isinstance(scope, metadata.GlobalScope):
        return children
    elif getattr(scope, "name", None) is None:
        # if scope.name is undefined OR explicitly set to None
        raise UnnamedScopeError(
            f"Cannot resolve name for unnamed scope: '{scope._name_prefix}'"
        )
    else:
        if not children:
            new_children = scope.name
        else:
            new_children = f"{scope.name}.{children}"
        return _resolve_scope_name(scope.parent, new_children)
