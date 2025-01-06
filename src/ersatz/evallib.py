
import builtins
import logging
from functools import wraps
from typing import Any, Type

import libcst as cst
from libcst import matchers as m
from RestrictedPython import compile_restricted_eval, safe_builtins, limited_builtins, utility_builtins


# this constant is not allcaps for naming consistency with RestrictedPython
type_builtins = {k:v for k,v in dict[str].items(builtins.__dict__) if isinstance(v, Type)}

class SafeEvaluationError(Exception):
    def __init__(self, expression: str, *args, **kwargs):
        super().__init__(f"Unsafe expression: {expression!r}", *args, **kwargs)
        self.expression = expression


def _concat_globals(*dicts: dict[str, Any]) -> dict[str, Any]:
    """Concatenate multiple dictionaries into one, and nest them under '__builtins__' key."""
    concat = dict()
    for d in dicts:
        concat.update(d)
    return {'__builtins__': concat}


def expression_contains_call(expr: str) -> bool:
    return bool(m.findall(cst.parse_expression(expr), m.Call()))


def annotation_eval(annotation: str, locals: dict[str] = None) -> Type:
    if expression_contains_call(annotation):
        raise ValueError("Calls inside annotations are not supported for security reasons.")
    return eval(annotation, _concat_globals(type_builtins), locals)


def safe_eval(expr: str, locals: dict[str] = None):
    """Safely evaluate an expression."""
    try:
        compiled = compile_restricted_eval(expr)
        if compiled.errors:
            raise SyntaxError(compiled.errors)
        return eval(
            compiled.code, 
            _concat_globals(safe_builtins, limited_builtins, utility_builtins),
            locals
        )
    except Exception as e:
        raise SafeEvaluationError(expr) from e
    

def safe_type_eval(expr: str, locals: dict[str] = None) -> Type:
    """Safely evaluate the data type of a given expression."""
    return type(safe_eval(expr, locals))


def try_safe_type_eval(expr: str, locals: dict[str] = None) -> Type | None:
    try:
        return safe_type_eval(expr, locals=locals)
    except Exception as e:
        logging.debug(f"Unable to evaluate dtype from '{expr}': {e}")
        return None


def try_annotation_eval(expr: str, locals: dict[str]=None) -> Type | None:
    try:
        return annotation_eval(expr, locals=locals)
    except Exception as e:
        logging.debug(f"Unable to evaluate dtype from annotation '{expr}': {e}")
        return None


def main() -> None:
    while (annotation := input("Type annotation: ")) != "bla":
        tpe = annotation_eval(annotation)
        print(tpe, type(tpe))


def _test():
    @wraps(annotation_eval)
    def eval_or_return_exception(*args, **kwargs):
        try: 
            return annotation_eval(*args, **kwargs)
        except Exception as e:
            return e
            
    
    cases  = {
        "int": int,
        "list": list,
        "list[int]": list[int],
        "xwdlkqj": NameError,
        "exit()": Exception,
        "from pathlib import Path; print(Path('requirements.txt').read_text())": Exception,
    }

    for arg, expected in cases.items():
        result = eval_or_return_exception(arg)
        valid = (result == expected) if not issubclass(expected, Exception) else isinstance(result, expected)
        print(f"{valid!s:5} {arg} -> {result} | {expected}")


if __name__ == "__main__":
    # main()
    _test()
    
