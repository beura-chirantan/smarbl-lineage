"""Immutable bidirectional lineage graph construction."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from types import MappingProxyType

from .errors import GraphBuildError, GraphValidationError, NodeParseError
from .expression_parser import ExpressionParser, ParseFailure, ParseSuccess
from .model import Node, normalize_node_id

_EMPTY_IDS: tuple[str, ...] = ()


def _query_id(value: object) -> str | None:
    try:
        return normalize_node_id(value)
    except (TypeError, ValueError):
        return None


class LineageGraph:
    """A read-only graph whose edges point from owner to dependency.

    Construction is atomic: every expression is parsed, all parse failures are
    reported together, and adjacency is only published if every node is valid.
    """

    def __init__(
        self,
        nodes: Iterable[Node],
        parser: ExpressionParser | None = None,
    ) -> None:
        node_list = tuple(nodes)
        nodes_by_id: dict[str, Node] = {}
        nodes_by_name: dict[str, Node] = {}

        for position, node in enumerate(node_list):
            if not isinstance(node, Node):
                raise GraphValidationError(
                    f"item {position} is not a Node: {type(node).__name__}"
                )
            if node.id in nodes_by_id:
                raise GraphValidationError(f"duplicate node id: {node.id!r}")
            if node.name in nodes_by_name:
                raise GraphValidationError(f"duplicate node name: {node.name!r}")
            nodes_by_id[node.id] = node
            nodes_by_name[node.name] = node

        expression_parser = parser or ExpressionParser()
        parsed_variables: dict[str, frozenset[str]] = {}
        failures: list[NodeParseError] = []

        for node in node_list:
            result = expression_parser.parse(node.expression)
            if isinstance(result, ParseFailure):
                failures.append(NodeParseError(node, result))
            elif isinstance(result, ParseSuccess):
                parsed_variables[node.id] = result.variables

        if failures:
            raise GraphBuildError(failures)

        mutable_uses = {node.id: set() for node in node_list}
        mutable_used_by = {node.id: set() for node in node_list}
        mutable_external = {node.id: set() for node in node_list}

        for node in node_list:
            for variable in parsed_variables[node.id]:
                dependency = nodes_by_name.get(variable)
                if dependency is None:
                    mutable_external[node.id].add(variable)
                    continue
                mutable_uses[node.id].add(dependency.id)
                mutable_used_by[dependency.id].add(node.id)

        def sort_ids(ids: set[str]) -> tuple[str, ...]:
            return tuple(
                sorted(ids, key=lambda node_id: (nodes_by_id[node_id].name, node_id))
            )

        uses_ordered = {
            node_id: sort_ids(dependencies)
            for node_id, dependencies in mutable_uses.items()
        }
        used_by_ordered = {
            node_id: sort_ids(dependents)
            for node_id, dependents in mutable_used_by.items()
        }

        self._nodes = node_list
        self._nodes_by_id: Mapping[str, Node] = MappingProxyType(nodes_by_id)
        self._nodes_by_name: Mapping[str, Node] = MappingProxyType(nodes_by_name)
        self._uses_ids: Mapping[str, tuple[str, ...]] = MappingProxyType(uses_ordered)
        self._used_by_ids: Mapping[str, tuple[str, ...]] = MappingProxyType(
            used_by_ordered
        )
        self._external: Mapping[str, frozenset[str]] = MappingProxyType(
            {
                node_id: frozenset(references)
                for node_id, references in mutable_external.items()
            }
        )
        self._edge_count = sum(len(ids) for ids in uses_ordered.values())

    @property
    def nodes(self) -> tuple[Node, ...]:
        return self._nodes

    @property
    def node_ids(self) -> tuple[str, ...]:
        return tuple(node.id for node in self._nodes)

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return self._edge_count

    def get_node(self, node_id: object) -> Node | None:
        normalized = _query_id(node_id)
        return self._nodes_by_id.get(normalized) if normalized is not None else None

    def get_node_by_name(self, name: str) -> Node | None:
        return self._nodes_by_name.get(name)

    def dependency_ids(self, node_id: object) -> tuple[str, ...]:
        normalized = _query_id(node_id)
        if normalized is None:
            return _EMPTY_IDS
        return self._uses_ids.get(normalized, _EMPTY_IDS)

    def dependent_ids(self, node_id: object) -> tuple[str, ...]:
        normalized = _query_id(node_id)
        if normalized is None:
            return _EMPTY_IDS
        return self._used_by_ids.get(normalized, _EMPTY_IDS)

    def get_uses(self, node_id: object) -> frozenset[Node]:
        return frozenset(
            self._nodes_by_id[dependency_id]
            for dependency_id in self.dependency_ids(node_id)
        )

    def get_used_by(self, node_id: object) -> frozenset[Node]:
        return frozenset(
            self._nodes_by_id[dependent_id]
            for dependent_id in self.dependent_ids(node_id)
        )

    # Descriptive aliases for callers who prefer graph terminology.
    dependencies_of = get_uses
    dependents_of = get_used_by

    def external_references(self, node_id: object) -> frozenset[str]:
        normalized = _query_id(node_id)
        if normalized is None:
            return frozenset()
        return self._external.get(normalized, frozenset())

    def find_paths(self, from_id: object, to_id: object) -> list[list[Node]]:
        from .path_finder import PathFinder

        return PathFinder(self).find_paths(from_id, to_id)
