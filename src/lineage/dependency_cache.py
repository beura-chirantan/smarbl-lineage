"""Eager transitive-closure cache backed by compact Python integer bitsets."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Set as AbstractSet
from types import MappingProxyType

from .errors import CycleError
from .graph import LineageGraph, _query_id
from .model import Node


class _NodeMaskSet(AbstractSet[Node]):
    """Immutable Set[Node] view over a precomputed reachability bit mask."""

    __slots__ = ("_index_by_id", "_mask", "_nodes")

    def __init__(
        self,
        mask: int,
        nodes: tuple[Node, ...],
        index_by_id: dict[str, int],
    ) -> None:
        self._mask = mask
        self._nodes = nodes
        self._index_by_id = index_by_id

    def __contains__(self, value: object) -> bool:
        if not isinstance(value, Node):
            return False
        index = self._index_by_id.get(value.id)
        return index is not None and bool(self._mask & (1 << index))

    def __iter__(self) -> Iterator[Node]:
        remaining = self._mask
        while remaining:
            lowest_bit = remaining & -remaining
            index = lowest_bit.bit_length() - 1
            yield self._nodes[index]
            remaining ^= lowest_bit

    def __len__(self) -> int:
        return self._mask.bit_count()

    @classmethod
    def _from_iterable(cls, iterable: Iterable[Node]) -> frozenset[Node]:
        """Make inherited set algebra return a regular immutable set."""

        return frozenset(iterable)

    def __repr__(self) -> str:
        return f"NodeSet({{{', '.join(repr(node) for node in self)}}})"


_EMPTY_RESULT: frozenset[Node] = frozenset()


class DependencyCache:
    """Validates acyclicity and stores both closures for every graph node.

    The closure payloads are precomputed integer masks. Each public result set
    is also created once during construction; repeated queries only perform a
    dictionary lookup and never traverse adjacency.
    """

    def __init__(self, graph: LineageGraph) -> None:
        self._graph = graph
        dependency_first = self._dependency_first_order(graph)

        nodes = graph.nodes
        index_by_id = {node.id: index for index, node in enumerate(nodes)}
        upstream_masks = [0] * len(nodes)
        downstream_masks = [0] * len(nodes)

        # Every dependency is ready before the node that consumes it.
        for node_id in dependency_first:
            index = index_by_id[node_id]
            mask = 0
            for dependency_id in graph.dependency_ids(node_id):
                dependency_index = index_by_id[dependency_id]
                mask |= (1 << dependency_index) | upstream_masks[dependency_index]
            upstream_masks[index] = mask

        # Reverse order makes every dependent ready before its dependency.
        for node_id in reversed(dependency_first):
            index = index_by_id[node_id]
            mask = 0
            for dependent_id in graph.dependent_ids(node_id):
                dependent_index = index_by_id[dependent_id]
                mask |= (1 << dependent_index) | downstream_masks[dependent_index]
            downstream_masks[index] = mask

        self._index_by_id = index_by_id
        self._upstream_masks = tuple(upstream_masks)
        self._downstream_masks = tuple(downstream_masks)
        self._upstream = MappingProxyType(
            {
                node.id: _NodeMaskSet(
                    upstream_masks[index], nodes, index_by_id
                )
                for index, node in enumerate(nodes)
            }
        )
        self._downstream = MappingProxyType(
            {
                node.id: _NodeMaskSet(
                    downstream_masks[index], nodes, index_by_id
                )
                for index, node in enumerate(nodes)
            }
        )

    @property
    def graph(self) -> LineageGraph:
        return self._graph

    def get_upstream(self, node_id: object) -> AbstractSet[Node]:
        normalized = _query_id(node_id)
        if normalized is None:
            return _EMPTY_RESULT
        return self._upstream.get(normalized, _EMPTY_RESULT)

    def get_downstream(self, node_id: object) -> AbstractSet[Node]:
        normalized = _query_id(node_id)
        if normalized is None:
            return _EMPTY_RESULT
        return self._downstream.get(normalized, _EMPTY_RESULT)

    def can_reach(self, from_id: object, to_id: object) -> bool:
        """Return whether ``to_id`` is in ``from_id``'s upstream closure."""

        source = _query_id(from_id)
        target = _query_id(to_id)
        if source is None or target is None:
            return False
        source_index = self._index_by_id.get(source)
        target_index = self._index_by_id.get(target)
        if source_index is None or target_index is None:
            return False
        return bool(self._upstream_masks[source_index] & (1 << target_index))

    @staticmethod
    def _dependency_first_order(graph: LineageGraph) -> tuple[str, ...]:
        """Iterative three-color DFS; returns postorder or raises with a cycle."""

        unseen, active, complete = 0, 1, 2
        state = {node_id: unseen for node_id in graph.node_ids}
        postorder: list[str] = []

        for start in graph.node_ids:
            if state[start] != unseen:
                continue

            state[start] = active
            path = [start]
            position = {start: 0}
            # Frames are (node ID, index of the next neighbor to inspect).
            stack: list[tuple[str, int]] = [(start, 0)]

            while stack:
                node_id, neighbor_index = stack[-1]
                neighbors = graph.dependency_ids(node_id)

                if neighbor_index >= len(neighbors):
                    stack.pop()
                    finished = path.pop()
                    position.pop(finished)
                    state[finished] = complete
                    postorder.append(finished)
                    continue

                dependency_id = neighbors[neighbor_index]
                stack[-1] = (node_id, neighbor_index + 1)
                dependency_state = state[dependency_id]

                if dependency_state == unseen:
                    state[dependency_id] = active
                    position[dependency_id] = len(path)
                    path.append(dependency_id)
                    stack.append((dependency_id, 0))
                elif dependency_state == active:
                    cycle_start = position[dependency_id]
                    cycle_ids = [*path[cycle_start:], dependency_id]
                    cycle_nodes = [
                        graph.get_node(cycle_id) for cycle_id in cycle_ids
                    ]
                    # All cycle IDs originated from the graph index.
                    raise CycleError(
                        [node for node in cycle_nodes if node is not None]
                    )

        return tuple(postorder)
