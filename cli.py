import types
import typing
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Literal, Type


from wrapper import AssignementWrapper, CodeWrapper
from evallib import safe_eval, try_annotation_eval, try_safe_type_eval


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
    argv: list = None, dtype_inference: DtypeInference = None
) -> Namespace:
    """Parse arguments from a script file.

    Every gobal assignement in the script file will be parsed as an argument, unless the comment contains "NO PARAM" or "no param".
    Depending on the dtype_inference, the type of the argument will be inferred from the annotation, the value, or both.

    Args:
        argv (list, optional): List of command-line arguments. Defaults to `sys.argv`.
        dtype_inference (Literal["none", "annotation", "value", "both"], optional): How to infer the data type of the arguments. Defaults to None.

    Returns:
        Namespace: Parsed arguments as a `Namespace` object.
    """
    base_parser = ArgumentParser(add_help=False)

    base_parser.add_argument("script", type=Path, help="path to the script to parse.")
    base_parser.add_argument(
        "--output", "-o", type=Path, help="path to the output file."
    )

    # ignore errors. exit_on_errors=False doesn't work for some reason
    base_parser.error = lambda s: None
    args, other_argv = base_parser.parse_known_args(args=argv)

    full_parser = ArgumentParser(
        parents=[base_parser],
        add_help=True,
        exit_on_error=True,
    )

    if getattr(args, "script", None) is not None and Path(args.script).exists():
        argument_group = full_parser.add_argument_group("Script options")

        wrapper = CodeWrapper.from_file(args.script)
        assignements = wrapper.analyze_assigns(wrapper.GLOBAL_SCOPE)

        for assignement in assignements:
            args, kwargs = assignement_to_args(
                assignement,
                dtype_inference=dtype_inference,
                default_type=RawExpr,
                nargs_classes=[list],
            )
            argument_group.add_argument(*args, **kwargs)

    return full_parser.parse_args()


def namespace_to_dict(arguments: Namespace) -> dict:
    return vars(arguments)


def get_set_arguments(arguments: Namespace) -> dict:
    return {k: v for k, v in namespace_to_dict(arguments).items() if v is not UNSET}


def _test():
    args = parse_arguments(dtype_inference="both")
    print(namespace_to_dict(args).keys())
    print(get_set_arguments(args))


if __name__ == "__main__":
    _test()
