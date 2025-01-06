from typing import Self
from pathlib import Path

from libcst import metadata, matchers as m
import libcst as cst

from .matchers import statement_matcher
from .node_converter import node_to_string, try_resolve_scope_name
from .transformers import Substitutor


class AssignementWrapper:
    def __init__(
        self, node: cst.SimpleStatementLine, metadata_wrapper: metadata.MetadataWrapper
    ) -> None:
        self._node = node
        self._metadata_wrapper = metadata_wrapper
        self._scope = metadata_wrapper.resolve(metadata.ScopeProvider)[node]

        # extract data
        data = m.extract(node, statement_matcher, metadata_resolver=metadata_wrapper)
        # mandatory fields
        self._name = data["name"]
        self._value = data["value"]
        # optional fields
        self._annotation = data.get("annotation")
        self._comment = data.get("comment")

    @property
    def name(self):
        return self._name

    @property
    def annotation(self):
        return self._annotation

    @property
    def value(self):
        return self._value

    @property
    def comment(self):
        return self._comment

    def scope_as_string(self) -> str:
        return try_resolve_scope_name(self._scope)

    def value_as_string(self) -> str:
        return node_to_string(self._value)

    def annotation_as_string(self) -> str | None:
        if self._annotation is None:
            return None
        return node_to_string(self._annotation)

    def __repr__(self):
        return f"<AssignementWrapper of {str(self)!r}>"

    def __str__(self):
        return node_to_string(self._node).strip()


class CodeWrapper:
    GLOBAL_SCOPE = ""
    ANY_SCOPE = None

    def __init__(self, code: str) -> None:
        self._update_wrapper(cst.parse_module(code))

    @classmethod
    def from_file(cls, file_path: str | Path) -> Self:
        file_path = Path(file_path)
        return cls(file_path.read_text())

    def _get_scopes(self) -> dict[str, metadata.Scope]:
        all_scopes = set(self.wrapper.resolve(metadata.ScopeProvider).values())
        return {
            scope_name: scope
            for scope in all_scopes
            if (scope_name := try_resolve_scope_name(scope)) is not None
        }

    @property
    def code(self) -> str:
        return node_to_string(self.wrapper.module)

    def _update_wrapper(self, module: cst.Module):
        self.wrapper = metadata.MetadataWrapper(module)

    def list_scope_names(self) -> list[str]:
        return list(self._get_scopes().keys())

    def analyze_assigns(self, scope_name: str = None) -> list[AssignementWrapper]:
        assignements = []
        for match in m.findall(self.wrapper, statement_matcher):
            assignement = AssignementWrapper(match, self.wrapper)
            if scope_name is None or assignement.scope_as_string() == scope_name:
                assignements.append(assignement)
        return assignements

    def _substitute_assign_values(
        self, mapping: dict[str, str], scope: metadata.Scope = None
    ) -> dict[str, str]:
        substitutor = Substitutor(mapping, scope)
        new_module = self.wrapper.visit(substitutor)
        self._update_wrapper(new_module)
        return substitutor.retrieve_non_substituted()

    def substitute_assign_values(self, mapping: dict[str, str], scope_name: str = None):
        if scope_name is self.ANY_SCOPE:
            scope = None
        else:
            scope = self._get_scopes()[scope_name]
        return self._substitute_assign_values(mapping, scope)

    def substitute_assign_values_global(self, mapping: dict[str, str]):
        return self.substitute_assign_values(
            scope_name=self.GLOBAL_SCOPE, mapping=mapping
        )


def _test():
    my_wrapper = CodeWrapper.from_file("test_data/test_script.py")

    print(my_wrapper.list_scope_names())
    from pprint import pprint

    pprint(my_wrapper.analyze_assigns(None))
    pprint(my_wrapper.analyze_assigns("MyClass"))
    pprint(
        my_wrapper.substitute_assign_values_global({"x": "1", "y": "2", "blabla": "3"})
    )
    pprint(my_wrapper.substitute_assign_values({"X": "12", "y": "5", "foo": "3"}))
    print(my_wrapper.code)


if __name__ == "__main__":
    _test()
