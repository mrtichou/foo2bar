import logging
import types
import typing
from argparse import ArgumentParser
from pathlib import Path
from typing import Literal, Type


import foo2bar.logging as logging
from foo2bar.logging import logger
from .wrapper import AssignementWrapper, CodeWrapper
from .evallib import safe_eval, try_annotation_eval, try_safe_type_eval


class RawExpr(str):
    def __repr__(self):
        return super().__str__()


class UNSET:
    def __repr__(self):
        return "UNSET"


UNSET = UNSET()


DtypeInference = Literal["none", "value", "annotation", "both"]


def interpret_dtype(
    assignement: AssignementWrapper,
    dtype_inference: DtypeInference,
    default_type: type,
    nargs_classes: list[Type] = None,
) -> dict:
    if nargs_classes is None:
        nargs_classes = []

    if dtype_inference is not None and dtype_inference not in typing.get_args(
        DtypeInference
    ):
        raise ValueError(
            f"dtype_inference must be one of {DtypeInference.__args__!r}, not {dtype_inference!r}"
        )

    dtype: Type | None = None
    if dtype_inference in ["annotation", "both"]:
        dtype = try_annotation_eval(assignement.annotation_as_string())
    if dtype_inference in ["value", "both"] and dtype is None:
        dtype = try_safe_type_eval(assignement.value_as_string())
    if dtype is None or dtype_inference in ["none", None]:
        dtype = default_type

    if isinstance(dtype, types.GenericAlias) and dtype.__origin__ in nargs_classes:
        return {
            "nargs": "*",
            "type": dtype.__args__[0],
        }
    else:
        return {
            "type": dtype,
        }


def build_argument_help(assignement: AssignementWrapper) -> str:
    comment: str = assignement.comment
    if comment is not None:
        comment = comment.lstrip("# ").strip()

    try:
        default_value = safe_eval(assignement.value_as_string())
        default_comment = f"Defaults to {default_value!r}"
    except Exception:
        default_comment = None

    total_comment = " ".join(
        [c.rstrip(". ") + "." for c in [comment, default_comment] if c is not None]
    )

    return total_comment or None


def assignement_to_args(
    assignement: AssignementWrapper,
    dtype_inference: DtypeInference,
    default_type: Type[str] | Type[RawExpr],
    nargs_classes: list[Type],
) -> tuple[list[str], dict]:
    args = ["--{}".format(assignement.name)]

    kwargs = {
        "default": UNSET,
        "metavar": assignement.name,
    }

    kwargs.update(
        interpret_dtype(
            assignement,
            dtype_inference=dtype_inference,
            default_type=default_type,
            nargs_classes=nargs_classes,
        )
    )

    kwargs["help"] = build_argument_help(assignement)

    return args, kwargs


def parse_arguments(
    argv: list = None
) -> dict:
    """Parse arguments from a script file.

    Every gobal assignement in the script file will be parsed as an argument, unless the comment contains "NO PARAM" or "no param".
    Depending on the dtype_inference, the type of the argument will be inferred from the annotation, the value, or both.

    Args:
        argv (list, optional): List of command-line arguments. Defaults to `sys.argv`.
        dtype_inference (Literal["none", "annotation", "value", "both"], optional): How to infer the data type of the arguments. Defaults to None.

    Returns:
        dict: A dictionary containing the script path, the output path, and the parsed arguments.
    """
    base_parser = ArgumentParser(add_help=False)

    base_parser.add_argument("script", type=Path, help="path to the script to parse.")
    base_parser.add_argument("mode", type=str, choices=["raw", "typed"], default="raw", help="argument type interpretation mode. See readme for more information.")
    base_parser.add_argument(
        "--output", "-o", type=Path, help="path to the output file."
    )
    
    # ignore errors. exit_on_errors=False doesn't work for some reason
    base_parser.error = lambda s: None
    base_args, other_argv = base_parser.parse_known_args(args=argv)
    dtype_inference = "none" if base_args.mode == "raw" else "both"
    
    script_parser = ArgumentParser(
        add_help=False,
        exit_on_error=False,
    )

    if getattr(base_args, "script", None) is not None and Path(base_args.script).exists():
        argument_group = script_parser.add_argument_group("script options")

        wrapper = CodeWrapper.from_file(base_args.script)
        assignements = wrapper.analyze_assigns(wrapper.GLOBAL_SCOPE)

        for assignement in assignements:
            args, kwargs = assignement_to_args(
                assignement,
                dtype_inference=dtype_inference,
                default_type=RawExpr,
                nargs_classes=[list],
            )
            argument_group.add_argument(*args, **kwargs)

    full_parser = ArgumentParser(
        parents=[base_parser, script_parser],
        add_help=True,
        exit_on_error=True,
    )
    
    # display help message if needed
    full_parser.parse_args(args=argv)
    
    return {
        **vars(base_args), # "mode", "script", "output"
        "arguments": vars(script_parser.parse_args(other_argv)), # all other arguments
    }

def substitute_global(script: Path, mapping: dict) -> tuple[str, dict[str, str]]:
    wrapper = CodeWrapper.from_file(script)
    
    remaining = wrapper.substitute_assign_values_global(mapping)
    
    return wrapper.code, remaining


def main():
    args = parse_arguments()
    logger.setLevel(logging.INFO)
    
    mapping = {k: v for k, v in args["arguments"].items() if v is not UNSET}
    
    if args["mode"] == "typed":
        mapping = {k: repr(v) for k, v in mapping.items()}
    
    new_script, remaining = substitute_global(
        script=args["script"], 
        mapping=mapping
    )
    
    if remaining:
        logger.warning("Some variables were not substituted:" + ", ".join(remaining.keys()))
    
    if isinstance(args["output"], Path):
        args["output"].write_text(new_script)
        logger.info(f"Script written to {args['output']}")
    else:
        print(new_script)

def _test():
    args = parse_arguments(dtype_inference="both")
    print(args.keys())
    print(args["arguments"].keys())
    print({k: v for k, v in args["arguments"].items() if v is not UNSET})


if __name__ == "__main__":
    _test()
