"""Typed errors raised by graph-level operations."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .expression_parser import ParseFailure
    from .model import Node


class LineageError(Exception):
    """Base class for expected application errors."""


class InputError(LineageError):
    """The input file is not valid lineage JSON."""


class GraphValidationError(LineageError):
    """Node identity constraints make a graph ambiguous or invalid."""


@dataclass(frozen=True, slots=True)
class NodeParseError:
    """Adds node context to a recoverable expression parse failure."""

    node: Node
    failure: ParseFailure


class GraphBuildError(LineageError):
    """One or more expressions were invalid; no partial graph was published."""

    def __init__(self, failures: Sequence[NodeParseError]) -> None:
        self.failures = tuple(failures)
        detail = "; ".join(
            f"node {item.node.id!r} ({item.node.name!r}): "
            f"{item.failure.message}"
            for item in self.failures
        )
        super().__init__(
            f"cannot build graph: {len(self.failures)} invalid expression(s): "
            f"{detail}"
        )


class CycleError(LineageError):
    """The dependency cache cannot be built for a cyclic graph."""

    def __init__(self, cycle: Sequence[Node]) -> None:
        self.cycle = tuple(cycle)
        rendered = " -> ".join(
            f"{node.name}[{node.id}]" for node in self.cycle
        )
        super().__init__(f"dependency cycle detected: {rendered}")
