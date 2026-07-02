"""Core immutable domain objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


NodeIdInput: TypeAlias = str | int


def normalize_node_id(value: object) -> str:
    """Normalize the two ID forms accepted by the supplied JSON example.

    The written contract says IDs are strings, while its JSON example uses an
    integer. Supporting both at the boundary avoids a surprising rejection.
    Booleans are deliberately rejected even though ``bool`` subclasses ``int``.
    """

    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise TypeError("node id must be a non-empty string or an integer")

    normalized = str(value)
    if not normalized:
        raise ValueError("node id must not be empty")
    return normalized


@dataclass(frozen=True, slots=True, eq=False)
class Node:
    """A lineage entity, identified and hashed by its normalized unique ID."""

    id: str
    name: str
    expression: str

    def __init__(self, id: NodeIdInput, name: str, expression: str) -> None:
        normalized_id = normalize_node_id(id)
        if not isinstance(name, str):
            raise TypeError("node name must be a string")
        if not name:
            raise ValueError("node name must not be empty")
        if not isinstance(expression, str):
            raise TypeError("node expression must be a string")

        object.__setattr__(self, "id", normalized_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "expression", expression)

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.id == other.id
